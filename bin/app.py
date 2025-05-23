import os
import re

from flask import Flask, render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import Form, StringField, DateField, RadioField, BooleanField, FieldList, FormField, HiddenField, SubmitField

from common import const, sql_shared_service
from slacksearch import search_message, search_settings, models


root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
bin_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))

# app = Flask(__name__, template_folder=os.path.join(bin_dir, 'slacksearch'), static_folder=os.path.join(bin_dir, 'slacksearch', 'static'))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'

class CheckboxItemForm(Form):
    """
    チェックボックス用Form
    """
    checked = BooleanField()
    label = StringField()
    item_id = HiddenField()


class SlackSearchForm(FlaskForm):
    """
    検索画面用Form
    """
    search_val = StringField(label='検索文字列')
    search_type = RadioField('search_type_and', choices=[
        ('01', 'AND検索'), ('02', 'OR検索')
    ])
    is_contains_reply = BooleanField(label='返信内容を含める')
    search_from_date = DateField(label='期間')
    search_to_date = DateField(label='')

    poster_list = FieldList(FormField(CheckboxItemForm), min_entries=0)
    public_channel_list = FieldList(FormField(CheckboxItemForm), min_entries=0)
    private_channel_list = FieldList(FormField(CheckboxItemForm), min_entries=0)
    im_channel_list = FieldList(FormField(CheckboxItemForm), min_entries=0)
    mpim_channel_list = FieldList(FormField(CheckboxItemForm), min_entries=0)

    search_button = SubmitField('検索', render_kw={'style': 'width: 7em; height: 3em'})


class SlackSearchResultForm(FlaskForm):
    """
    検索結果画面用Form
    """
    search_val = HiddenField()
    data_count = StringField()
    channel_type = HiddenField()
    channel_name = HiddenField()
    post_date = HiddenField()


class SlackSearchDetailForm(FlaskForm):
    """
    詳細画面用Form
    """
    search_val = HiddenField()
    post_date = StringField('投稿日')
    post_icon = HiddenField()
    post_name = StringField('投稿者')
    post_message = StringField('メッセージ')


class SlackSearchSettingsForm(FlaskForm):
    """
    検索設定画面Form
    """
    regist_button = SubmitField('登録', render_kw={'style': 'width: 7em; height: 3em'})


@app.route('/index')
def index():
    """
    初期表示

    Returns:

    """

    with sql_shared_service.get_connection(root_dir) as conn:
        poster_list = search_message.get_poster_list(conn)
        channel_list = search_message.get_channel_list(conn)

    form = SlackSearchForm()
    # 検索タイプ
    form.search_type.data = '01'
    # 返信内容を含める
    form.is_contains_reply.data = True
    # 投稿者/返信者
    for poster in poster_list:
        entry = form.poster_list.append_entry()
        entry.label.data = poster['display_name']
        entry.item_id.data = poster['slack_user_id']
        if poster['checked']:
            entry.checked.data = True
    # channel
    for channel in channel_list:
        if channel['channel_type'] == const.PUBLIC_CHANNEL:
            entry = form.public_channel_list.append_entry()
        elif channel['channel_type'] == const.PRIVATE_CHANNEL:
            entry = form.private_channel_list.append_entry()
        elif channel['channel_type'] == const.IM_CHANNEL:
            entry = form.im_channel_list.append_entry()
        elif channel['channel_type'] == const.MPIM_CHANNEL:
            entry = form.public_channel_list.append_entry()
        else:
            continue
        entry.label.data = channel['channel_name']
        entry.item_id.data = channel['channel_id']
        if channel['checked']:
            entry.checked.data = True

    return render_template('index.html', form = form)


@app.route('/search', methods=['POST'])
def search():
    """
    検索

    Returns:

    """
    form = SlackSearchForm(request.form)
    model = _convert_search_model(form)
    with sql_shared_service.get_connection(root_dir) as conn:
        result_list = search_message.search(conn, model)

    # アイコンを設定
    for record in result_list:
        record['post_icon'] = url_for('static', filename=f'icon/{record["post_name"]}.jpg')

    result_form = SlackSearchResultForm()
    result_form.search_val = form.search_val
    result_form.data_count.data = f'{len(result_list):,}'

    return render_template('result.html', form=result_form, result_list=result_list)


@app.route('/detail', methods=['POST'])
def detail():
    """
    詳細

    Returns:

    """
    form = SlackSearchResultForm(request.form)
    model = _convert_detail_model(form)
    result = search_message.get_detail(root_dir, model)

    # アイコンを設定
    for record in result.result_list:
        record['reply_icon'] = url_for('static', filename=f'icon/{record["reply_name"]}.jpg')

    detail_form = SlackSearchDetailForm()
    detail_form.post_date.data = result.post_date
    detail_form.post_icon.data = url_for('static', filename=f'icon/{result.post_name}.jpg')
    detail_form.post_name.data = result.post_name
    detail_form.post_message.data = result.post_message

    return render_template('detail.html', form=detail_form, result_list=result.result_list)


@app.route('/settings', methods=['GET'])
def index_settings():
    """
    初期表示(設定)

    Returns:

    """
    form = SlackSearchSettingsForm(request.form)
    with sql_shared_service.get_connection(root_dir) as conn:
        poster_list_ = search_settings.get_poster_list(conn)
        channel_list_ = search_settings.get_channel_list(conn)

    # 投稿者/返信者
    poster_list = []
    index = 1
    for _, record in poster_list_.iterrows():
        poster_list.append({
            'index': str(index),
            'slack_user_id': record['slack_user_id'],
            'user_id': record['user_id'],
            'user_name': record['user_name'],
            'checked_display': 'checked' if record['display_flg'] == 1 else '',
            'checked_check': 'checked' if record['default_check_flg'] == 1 else '',
        })
        index += 1

    # channel
    channel_list = []
    index = 1
    for _, record in channel_list_.iterrows():
        channel_list.append({
            'index': str(index),
            'channel_id': record['channel_id'],
            'channel_name': record['channel_name'],
            'channel_type': record['channel_type'],
            'checked_display': 'checked' if record['display_flg'] == 1 else '',
            'checked_check': 'checked' if record['default_check_flg'] == 1 else '',
        })
        index += 1

    return render_template('indexSettings.html', form=form, poster_list=poster_list, channel_list=channel_list)


@app.route('/registSettings', methods=['POST'])
def regist_settings():
    """
    検索設定登録

    Returns:

    """
    poster_display_selected = request.form.getlist('poster_display')
    poster_check_selected = request.form.getlist('poster_check')
    channel_display_selected = request.form.getlist('channel_display')
    channel_check_selected = request.form.getlist('channel_check')

    # 登録
    with sql_shared_service.get_connection(root_dir) as conn:
        search_settings.regist(conn, poster_display_selected, poster_check_selected, channel_display_selected, channel_check_selected)

    return redirect(url_for('index_settings'))


def _convert_search_model(form: SlackSearchForm) -> models.SlackSearchModel:
    """
    検索用モデルへマッピング

    Args:
        form:

    Returns:

    """
    return models.SlackSearchModel(
        form.search_val.data,
        re.split(r'[ 　]+', form.search_val.data) if form.search_val.data else [],
        form.search_type.data,
        form.is_contains_reply.data,
        [entry.item_id.data for entry in form.poster_list if entry.checked.data],
        [entry.item_id.data for entry in form.public_channel_list if entry.checked.data],
        [entry.item_id.data for entry in form.private_channel_list if entry.checked.data],
        [entry.item_id.data for entry in form.im_channel_list if entry.checked.data],
        [entry.item_id.data for entry in form.mpim_channel_list if entry.checked.data],
        form.search_from_date.data,
        form.search_to_date.data,
    )

def _convert_detail_model(form: SlackSearchResultForm) -> models.SlackDetailModel:
    """
    詳細用モデルへマッピング

    Args:
        form:

    Returns:

    """
    return models.SlackDetailModel(
        form.channel_type.data,
        form.channel_name.data,
        form.post_date.data,
        form.search_val.data,
        re.split(r'[ 　]+', form.search_val.data),
    )


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5100, debug=True)
