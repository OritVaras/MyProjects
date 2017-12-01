from flask import Flask, jsonify, request, make_response, abort

app = Flask(__name__)

networks_dict = {}


def set_avg_throughput(network, throughput):
    old_throughput = float(network['avg_throughput'])
    network['avg_throughput'] = old_throughput + (
            (throughput - old_throughput) / len(network['devices']))


def isfloat(value):
    try:
        float(value)
        return True
    except:
        return False


@app.route('/')
def index():
    return "rest_wifi_task"


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/my-service/api/network', methods=['GET'])
def fetch():
    id = request.args.get('id')
    if id in networks_dict:
        return jsonify(networks_dict[id])
    else:
        abort(404)


@app.route('/my-service/api/network/connect', methods=['PUT'])  # remove printouts
def connect():
    if not request.json or not 'network_id' in request.json:
        abort(400)
    network_id = request.json['network_id']
    if network_id in networks_dict:  # Add device
        if 'device_id' in request.json:
            net_data = networks_dict[network_id]
            device_id = request.json['device_id']
            if not any(d.get('id', None) == device_id for d in net_data['devices']):
                net_data['devices'].append({'id': device_id})
            return jsonify(net_data)
        else:  # no device in request - bad request
            abort(400)
    else:  # Add network
        network = {
            'id': network_id,
            'auth': request.json.get('auth', "public"),
            'avg_throughput': '0',
            'devices': []
        }
        if 'device_id' in request.json:
            network['devices'].append({'id': request.json['device_id']})
        networks_dict[network_id] = network
    return jsonify({'network': networks_dict.values()}), 201


@app.route('/my-service/api/network/report', methods=['POST'])  # remove printouts
def report():
    if not request.json or not 'network_id' in request.json or not 'device_id' in request.json:
        abort(400)
    network_id = request.json['network_id']
    if not network_id in networks_dict:
        abort(404)
    net_data = networks_dict[network_id]
    device_id = request.json['device_id']
    if not any(d.get('id', None) == device_id for d in net_data['devices']):
        abort(404)
    # assuming each device reports throughput once - else it avg value is wrong
    if 'throughput' in request.json and isfloat(request.json['throughput']):
        set_avg_throughput(net_data, request.json['throughput'])

    return jsonify({'network': networks_dict.values()}), 200


if __name__ == "__main__":
    app.run()
