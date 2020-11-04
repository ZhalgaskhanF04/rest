from flask import Flask, jsonify, request, render_template
import random
import cx_Oracle
import logging
from datetime import datetime

app = Flask(__name__)

logging.basicConfig(filename="file.log",
					format='%(asctime)s %(message)s',
					filemode='a')
logger=logging.getLogger()

#Function to generate UNID

def get_uniqeid(num_chars):
	 code_chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
	 code = ''
	 for i in range(0, num_chars):
		 slice_start = random.randint(0, len(code_chars) - 1)
		 code += code_chars[slice_start: slice_start + 1]
	 return code

 #Function checks does loan_application exists in db usnig iin of client, with other credentials

def check_IIN(iin,fname,lname,mname,numdocument,cursor):
	try:
		query = cursor.execute("select iin,fname,numdocument from EC_ACTIVE where iin={}".format(iin))
		response = []
		for row in query:
			response.append(row)
		if iin in response[0][0] and fname in response[0][1] and numdocument in response[0][2]:
			return True
		else:
			return False
	except:
		return False

@app.route('/create', methods=['GET','POST'])
def loan_application():	
	#Connection to DB
	userpwd='l0tususer'
	connection = cx_Oracle.connect("lotususer", userpwd, "rnndb-1.fortebank.com:1521/rnn", encoding="UTF-8")
	cursor = connection.cursor()
	#getting the input parameters from request
	sIIN = request.args.get("IIN")
	sSourceBase = request.args.get("SourceBase")
	sFName = request.args.get("FName")
	sLName = request.args.get("LName")
	sMName = request.args.get("MName")
	sBDate = request.args.get("BDate")
	sNumDocument = request.args.get("NumDocument")
	#Date created generated auto
	sDateCreated = datetime.today().strftime('%d.%m.%Y')
	sUNID = get_uniqeid(32)
	#check if all parameters right, check if such application exist. If NOT create new one

	if check_IIN(sIIN,sFName,sLName,sMName,sNumDocument,cursor)==True:
		query = cursor.execute("select id,datecreated,sourcebase from EC_ACTIVE where iin={}".format(sIIN))
		response = []
		for row in query:
			response.append(row)
		#logging.info("")
		return jsonify({
						"Message":"В базе уже существует Кредитная заявка с такими данными",
						"Parameters":{
						"ID":"{}".format(response[0][0]),
						"ИИН":"{}".format(sIIN),
						"Имя":"{}".format(sFName),
						"Фамилия":"{}".format(sLName),
						"Номер документа":"{}".format(sNumDocument),
						"Источник заявки":"{}".format(response[0][2]),
						"Дата создания":"{}".format(response[0][1])
						}
						}
						)

		try:
			cursor.callproc('EC_START_ACTIVE_IIN',[1,sIIN,sSourceBase,sFName,sLName,sMName,sBDate,sDateCreated,sNumDocument,sUNID,''])
			connection.commit()
			connection.close()

		#connection 2 to check does it was succesdully added to db

			connection2 = cx_Oracle.connect("lotususer", userpwd, "rnndb-1.fortebank.com:1521/rnn", encoding="UTF-8")
			cursor2 = connection2.cursor()
			q = cursor2.execute("select id from ec_active where IIN={} order by datecreated desc".format(sIIN))
			resultID = []
			for row in q:
				print(row[0])
				resultID.append(row[0])
			connection2.close()
			return jsonify({"Message":"Кредитная заявка успешно записана",
									"Parameters":{
									"ID":"{}".format(str(resultID[0]))
									}
									}
									)
		except cx_Oracle.Error as e:
			message = str(e)
			a1 = message[11:5]# Error Message
			a2 = message[65:76]# source of loan_application
			a3 = message[78:81]# date created of this loan_application
			return jsonify({"Message":a1,
				"Источник заявки":a3,
				"Дата создания": a2
				})

@app.route('/delete', methods=['GET','POST'])
def loan_application_delete():
	userpwd='l0tususer'
	connection = cx_Oracle.connect("lotususer", userpwd, "rnndb-1.fortebank.com:1521/rnn", encoding="UTF-8")
	cursor = connection.cursor()
	nID = int(request.args.get("ID"))
	try:
		cursor.callproc('EC_END_ACTIVE',[nID])
		connection.commit()
		connection.close()
		return jsonify({"Message":"Кредитная заявка успешно удалена",
			"Parameters":{
			"ID":"{}".format(nID)
			}
			}
			)

	except cx_Oracle.Error as error:
		return jsonify({"Message":"{}".format(error)
			   })

if __name__ == '__main__':
	app.run(debug=True, host="0.0.0.0",port=8080)