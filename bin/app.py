import os
import re

from flask import Flask, render_template, url_for, request
from flask_wtf import FlaskForm
from wtforms import Form, StringField, DateField, RadioField, BooleanField, FieldList, FormField, HiddenField

from slacksearch import search_message, models


root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
bin_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))

# app = Flask(__name__, template_folder=os.path.join(bin_dir, 'slacksearch'), static_folder=os.path.join(bin_dir, 'slacksearch', 'static'))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'

class CheckboxItemForm(Form):
    checked = BooleanField()
    label = StringField()
    item_id = HiddenField()


class SlackSearchForm(FlaskForm):
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


class SlackSearchResultForm(FlaskForm):
    search_val = HiddenField()
    data_count = StringField()
    channel_type = HiddenField()
    channel_name = HiddenField()
    post_date = HiddenField()


@app.route('/index')
def index():
    """
    初期表示

    Returns:

    """

    poster_list = search_message.get_poster_list(root_dir, bin_dir)
    public_channel_list = search_message.get_channel_list(root_dir, bin_dir, 'public')
    private_channel_list = search_message.get_channel_list(root_dir, bin_dir, 'private')
    im_channel_list = search_message.get_channel_list(root_dir, bin_dir, 'im')

    form = SlackSearchForm()
    # 検索タイプ
    form.search_type.data = '01'
    # 返信内容を含める
    form.is_contains_reply.data = True
    # 投稿者/返信者
    for poster in poster_list:
        entry = form.poster_list.append_entry()
        entry.label.data = poster['display_name']
        entry.item_id.data = poster['user_id']
        if poster['checked']:
            entry.checked.data = True
    # channel(public)
    for channel in public_channel_list:
        entry = form.public_channel_list.append_entry()
        entry.label.data = channel['channel_name']
        entry.item_id.data = channel['channel_name']
        if channel['checked']:
            entry.checked.data = True
    # channel(private)
    for channel in private_channel_list:
        entry = form.private_channel_list.append_entry()
        entry.label.data = channel['channel_name']
        entry.item_id.data = channel['channel_name']
        if channel['checked']:
            entry.checked.data = True
    # channel(im)
    for channel in im_channel_list:
        entry = form.im_channel_list.append_entry()
        entry.label.data = channel['channel_name']
        entry.item_id.data = channel['channel_name']
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
    result_list = search_message.search(root_dir, model)

    # アイコンを設定
    for record in result_list:
        record['post_icon'] = url_for('static', filename=f'icon/{record["post_name"]}.jpg')

    result_form = SlackSearchResultForm()
    result_form.search_val = form.search_val
    result_form.data_count.label = str(len(result_list))

    return render_template('result.html', form=result_form, result_list=result_list)


@app.route('/detail', methods=['POST'])
def detail():
    """
    詳細

    Returns:

    """
    model = _convert_detail_model(request.form)
    result = search_message.get_detail(root_dir, model)

    # アイコンを設定
    result.post_icon = url_for('static', filename=f'icon/{result.post_name}.jpg')
    for record in result.result_list:
        record['reply_icon'] = url_for('static', filename=f'icon/{record["reply_name"]}.jpg')

    return render_template('detail.html', form=result)


def _convert_search_model(form: SlackSearchForm) -> models.SlackSearchModel:
    """
    検索用モデルへマッピング

    Args:
        form:

    Returns:

    """
    return models.SlackSearchModel(
        form.search_val.data,
        re.split(r'[ 　]+', form.search_val.data),
        form.search_type.data,
        form.is_contains_reply.data,
        [entry.item_id.data for entry in form.poster_list if entry.checked.data],
        [entry.item_id.data for entry in form.public_channel_list if entry.checked.data],
        [entry.item_id.data for entry in form.private_channel_list if entry.checked.data],
        [entry.item_id.data for entry in form.im_channel_list if entry.checked.data],
        form.search_from_date.data,
        form.search_to_date.data,
    )

def _convert_detail_model(form) -> models.SlackDetailModel:
    """
    詳細用モデルへマッピング

    Args:
        form:

    Returns:

    """
    return models.SlackDetailModel(
        form['channel_type'],
        form['channel_name'],
        form['post_date'],
        form['search_val'],
        re.split(r'[ 　]+', form['search_val']),
    )


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5100, debug=True)
