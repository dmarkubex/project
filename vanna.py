from vanna.remote import VannaDefault
vn = VannaDefault(model='chinook', api_key='5a3ee2062e8d4818ad1dce27df9dc3e8')
vn.connect_to_sqlite('https://vanna.ai/Chinook.sqlite')
vn.ask('What are the top 10 artists by sales?')

from vanna.flask import VannaFlaskApp
VannaFlaskApp(vn).run()