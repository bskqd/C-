Устанавливаем гит, клонируем репо<br>
<code>apt-get install git</code><br>
<code>git clone git@93.170.1.18:nastya/ac-back.git</code>

Устанавливаем postgres<br>
<code>sudo apt-get install python3-wheel postgresql  python-psycopg2 libpq-dev python3-dev python3-pip redis-server unoconv</code><br>
<code>apt-get install python3 python-dev python3-dev      build-essential libssl-dev libffi-dev      libxml2-dev libxslt1-dev zlib1g-dev      python-pip</code><br>
sudo apt-get install build-essential libssl-dev libffi-dev python-dev
Устанавливаем pip<br>
<code>apt-get install python-pip python3-pip</code>

Редактируем unoconv для работы с virtualenv
Edit the first line of <code>/usr/bin/unoconv</code> to replace:
<code>#!/usr/bin/env python3</code>
with
<code>#!/usr/bin/python3</code>

Устанавливаем зависимости.<br>
<code>В корне проекта pip3 install -r requirements.txt</code>

Устанавливаем pgcrypto в postgresql<br>
Заходим в постгре базу и добавляем расширение <br>
<code>sudo su<br>
sudo postgres <br>
psql itcs_main<br>
CREATE EXTENSION pgcrypto;</code>

Делаем миграции<br><code>
python3 manage.py makemigrations<br>
python3 manage.py migrate</code>
Test test