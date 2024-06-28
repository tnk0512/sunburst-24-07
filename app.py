from flask import Flask, render_template, jsonify, request
import json

app = Flask(__name__)

# JSONデータを読み込む関数
def load_viruses():
    with open('dataset/viruses.json') as f:
        return json.load(f)

# 特定のノードから深さ5までのノードを取得する関数
def get_subtree_with_parent(root, target_name, depth=5):
    def find_node_with_parent(node, name, parent=None):
        if node['name'] == name:
            return node, parent
        if 'children' in node:
            for child in node['children']:
                result = find_node_with_parent(child, name, node)
                if result:
                    return result
        return None, None

    def prune_tree(node, current_depth, max_depth):
        if current_depth >= max_depth:
            node.pop('children', None)
        elif 'children' in node:
            for child in node['children']:
                prune_tree(child, current_depth + 1, max_depth)

    target_node, parent_node = find_node_with_parent(root, target_name)
    if target_node:
        prune_tree(target_node, 0, depth)
        return target_node, parent_node
    return None, None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    viruses = load_viruses()
    return jsonify(viruses)

@app.route('/subtree', methods=['POST'])
def subtree():
    data = request.json
    target_name = data.get('target_name')
    viruses = load_viruses()
    subtree, parent_node = get_subtree_with_parent(viruses, target_name)
    if subtree:
        return jsonify({'subtree': subtree, 'parent': parent_node})
    return jsonify({'error': 'Node not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)