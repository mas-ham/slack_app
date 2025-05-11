import os

from flask import Flask, render_template, request

from slacksearch import search_message


root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
bin_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))

app = Flask(__name__, template_folder=os.path.join(bin_dir, 'slacksearch'), static_folder=os.path.join(bin_dir, 'icon'))

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
    result_list = search_message.search(root_dir, **request.form)

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
    post_date, post_name, post_message, result_list = search_message.get_detail(
        root_dir,
        request.form['channel_type'],
        request.form['channel_name'],
        request.form['post_date'],
        request.form['search_val']
    )

    return render_template(
        'detail.html',
        post_date=post_date,
        post_name=post_name,
        post_message=post_message,
        result_list=result_list
    )

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8888, debug=True)
