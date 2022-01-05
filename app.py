from flask import Flask, escape, url_for

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/user/<name>')
def user_page(name):
    return 'User: %s' % escape(name)


@app.route('/test')
def test_url_for():
    # 下面是一些调用命令（请在命令行窗口查看输出的 URL）
    print(url_for('hello_world'))

    print(url_for('user_page', name='lanye'))
    print(url_for('user_page', name='peter'))
    print(url_for('test_url_for'))
    # 下面这个调用传入了多余的关键字参数，它们会被作为查询字符串附加到 URL 后面。
    print(url_for('test_url_for', num=2))
    return 'Test Page'


if __name__ == '__main__':
    app.run()
