import os
import sqlite3
import datetime
from string import Template


root_path = os.path.dirname(os.path.abspath(__file__))


def get_link(user_agent, ip_address):
    conn = sqlite3.connect('sqlite.db')
    c = conn.execute('SELECT * FROM link WHERE is_clicked = 0 ORDER BY id DESC')
    data = c.fetchone()
    conn.execute(
        'INSERT INTO link_log (link_id, action, user_agent, ip_address, logged_at) VALUES (?,?,?,?,?)',
        (data[0], 'visit', user_agent, ip_address, datetime.datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()
    return data


def get_redirect(link_id, user_agent, ip_address):
    conn = sqlite3.connect('sqlite.db')
    c = conn.execute('SELECT * FROM link WHERE id=? AND is_clicked=0', (link_id,))
    data = c.fetchone()
    if data:
        conn.execute(
            'INSERT INTO link_log (link_id, action, user_agent, ip_address, logged_at) VALUES (?,?,?,?,?)',
            (link_id, 'click', user_agent, ip_address, datetime.datetime.utcnow().isoformat())
        )
        conn.execute('UPDATE link SET is_clicked = 1 WHERE id=?', (link_id,))
    conn.commit()
    conn.close()
    return data


def get_page(template_name, **kwargs):
    tpl = Template(open(os.path.join(root_path, 'templates', template_name), 'r').read())
    return tpl.substitute(**kwargs)


def user_meta(env):
    try:
        ip_addr = env['HTTP_X_FORWARDED_FOR'].split(',')[-1].strip()
    except KeyError:
        ip_addr = env.get('REMOTE_ADDR', None)
    return {
        'user_agent': env.get('HTTP_USER_AGENT', None),
        'ip_address': ip_addr
    }


def application(env, response):
    if env['PATH_INFO'] == '' or env['PATH_INFO'] == '/':
        response('200 OK', [('Content-Type', 'text/html')])
        return [bytes(get_page('index.html', link=get_link(**user_meta(env))[0]), encoding='utf-8')]
    elif 'redirect' in env['PATH_INFO']:
        query = env.get('QUERY_STRING', None)
        if query:
            parts = query.split('=')
            if len(parts) == 2 and parts[0] == 'link' and int(parts[1]):
                redirect = get_redirect(
                    int(parts[1]),
                    **user_meta(env)
                )
                if redirect:
                    # response('200 OK', [('Content-Type', 'text/plain')])
                    # return bytes(redirect[1], encoding='utf-8')
                    response('302 Found', [('Location', redirect[1])])
                    return
    response('404 Not Found', [('Content-Type', 'text/html')])
    return [bytes(get_page('404.html'), encoding='utf-8')]


if __name__ == '__main__':
    print("**********************************************************")
    print("Latest link visit:")
    print(get_link(user_agent='local_script', ip_address='127.0.0.1'))
    print("**********************************************************")
    print("Run uwsgi server using:")
    print("uwsgi --http :9090 --wsgi-file server.py")
