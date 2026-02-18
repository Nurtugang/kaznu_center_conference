### Conference

Requirements:
1. Python 3.10
2. requirements.txt
3. LibreOffice (soffice)
4. npm 10.9.0
5. package.json && package-lock.json
6. GNU gettext 0.25


### Step by step installation (Samson can skip steps 7,8):
1. git clone https://github.com/Nurtugang/kaznu_center_conference.git
2. source venv/bin/activate (Linux) or venv\Scripts\activate (Windows)
3. ``pip install -r requirements.txt``
4. Install npm dependencies (only tailwind here i guess) ``npm install`` and build css ``npm run build``
5. Apply migrations ``python manage.py migrate``
6. Apply translations texts, for that u need GNU gettext 0.25 installed in my machine, u can skip this if u dont need translations, default is Russian ``python manage.py compilemessages``
7. Install Libreoffice (soffice), I use it to convert docx to pdf using subprocess in conferences/models.py. **You also can skip this part, I just give you pdfs**
8. Configure .env. **I'll just send mine** 
9. Copy media/ folder, .env and db.sqlite3 that I sent you. **Copy db.sqlite3 only after migration.**
10. ``python manage.py runserver``

TODO:
1. https://tourismforum.ecokazwest.kz/index.php/documentation/ here if u tap button **PROCEEDINGS OF THE FORUM** 3d book will open. You must inplement the same 3d book viewer in templates/proceedings.html,  **proceeding_pdf** variable is passed to this html
2. Ваша работа успешно принята и отправлена на проверку! Текста в месседжах и в формах. Transalte those text
3. Сделать так чтобы система принимала только одну конференцию
4. Сделать так чтобы система генерировала только один сборник 