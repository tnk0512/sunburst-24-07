from flask import Flask, jsonify, render_template, request, send_file
import os
import pandas as pd
import numpy as np
import json

app = Flask(__name__)

# CSVデータをpandas DataFrameに読み込む関数
def load_data():
    df = pd.read_csv('static/dataset/viruses_withValue.csv')
    return df

# 深さ4のサブツリーを取得する関数
def get_subtree(target, df):
    def find_subtree(df, node, depth, max_depth=4):
        if depth > max_depth:
            return None
        children = df[df['parent'] == node['n']]
        subtree = {
            'n': int(node['n']),  # intに変換
            'name': node['name'],
            'parent': int(node['parent']),  # intに変換
            'value': node['value'],
            'children': []
        }
        for _, child in children.iterrows():
            child_subtree = find_subtree(df, child, depth + 1, max_depth)
            if child_subtree:
                subtree['children'].append(child_subtree)
        return subtree

    target_node = df[df['name'] == target].iloc[0]
    subtree = find_subtree(df, target_node, 0)
    return subtree

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_image', methods=['GET'])
def get_image():
    image_path = os.path.join('static', 'images', 'overview_viruses.png')
    return send_file(image_path, mimetype='image/png')

@app.route('/data', methods=['POST'])
def get_data():
    df = load_data()
    root_node = df[df['parent'] == -1].iloc[0]
    subtree = get_subtree(root_node['name'], df)
    return jsonify(json.loads(json.dumps(subtree, cls=NpEncoder)))

@app.route('/subtree', methods=['POST'])
def get_subtree_route():
    target_name = request.json.get('target_name')
    df = load_data()
    subtree = get_subtree(target_name, df)
    if subtree:
        parent_node = find_parent(df, target_name)
        return jsonify({'subtree': json.loads(json.dumps(subtree, cls=NpEncoder)), 'parent': parent_node})
    else:
        return jsonify({'error': 'Subtree not found'}), 404

def find_parent(df, target_name):
    target_node = df[df['name'] == target_name].iloc[0]
    parent_node = df[df['n'] == target_node['parent']]
    if not parent_node.empty:
        parent = parent_node.iloc[0].to_dict()
        parent['n'] = int(parent['n'])  # intに変換
        parent['parent'] = int(parent['parent'])  # intに変換
        return parent
    return None

if __name__ == '__main__':
    app.run(debug=True)
