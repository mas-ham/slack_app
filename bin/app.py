import os
import re

from flask import Flask, render_template, url_for, request

from slacksearch import search_message, models


root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
bin_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))

# app = Flask(__name__, template_folder=os.path.join(bin_dir, 'slacksearch'), static_folder=os.path.join(bin_dir, 'slacksearch', 'static'))
app = Flask(__name__)

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

    return render_template(
        'index.html',
        poster_list=poster_list,
        public_channel_list=public_channel_list,
        private_channel_list=private_channel_list,
        im_channel_list=im_channel_list
    )


@app.route('/search', methods=['POST'])
def search():
    """
    検索

    Returns:

    """
    model = _convert_search_model(request.form)
    result_list = search_message.search(root_dir, model)

    # アイコンを設定
    for record in result_list:
        record['post_icon'] = url_for('static', filename=f'icon/{record["post_name"]}.jpg')

    return render_template(
        'result.html',
        result_list=result_list,
        data_count=str(len(result_list)),
        search_val=request.form['search_val']
    )


@app.route('/detail', methods=['POST'])
def detail():
    """
    詳細

    Returns:

    """
    model = _convert_detail_model(request.form)
    post_date, post_name, post_message, result_list = search_message.get_detail(root_dir, model)

    # アイコンを設定
    post_icon = url_for('static', filename=f'icon/{post_name}.jpg')
    for record in result_list:
        record['reply_icon'] = url_for('static', filename=f'icon/{record["reply_name"]}.jpg')

    return render_template(
        'detail.html',
        post_date=post_date,
        post_icon=post_icon,
        post_name=post_name,
        post_message=post_message,
        result_list=result_list
    )


def _convert_search_model(form) -> models.SlackSearchModel:
    return models.SlackSearchModel(
        form['search_val'],
        re.split(r'[ 　]+', form['search_val']),
        form['search_type'],
        form['is_contains_reply'] if 'is_contains_reply' in form else False,
        _convert_list(form['poster_list']),
        _convert_list(form['public_channel_list']),
        _convert_list(form['private_channel_list']),
        _convert_list(form['im_channel_list']),
        form['search_from_date'],
        form['search_to_date'],
    )

def _convert_detail_model(form) -> models.SlackDetailModel:
    return models.SlackDetailModel(
        form['channel_type'],
        form['channel_name'],
        form['post_date'],
        form['search_val'],
        re.split(r'[ 　]+', form['search_val']),
    )


def _convert_list(joined_val):
    return joined_val.split(',') if joined_val else []


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8888, debug=True)
