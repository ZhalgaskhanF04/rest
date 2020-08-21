from flask import Flask, jsonify, request

app = Flask(__name__)

def func(RuId,RequestId,Lin):
	status = "200"
	pd = 1.0
	inc1 = 100
	inc2 = 200
	#Outpyt response format 
	response = [
    	{
      	  'RequestId': RequestId,
       		'StatusCode': status,
      	  'PD': pd, 
      	  'IncomeSn1': inc1,
      	  'IncomeSn2': inc2
    	}
		]
	return response


@app.route('/index', methods=['GET'])
def get_tasks():
		RuId = request.args.get("Ruid")
		RequestId = request.args.get("Requestid")
		Lin = request.args.get("Lin")
		responseServer = func(RuId,RequestId,Lin)
		return jsonify({'index': responseServer})

if __name__ == '__main__':
    app.run(debug=True)
