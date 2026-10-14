#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
光压云盘开发者 API - 后端服务
封装文档中全部 10 个接口，提供统一的签名鉴权
"""

import hashlib
import json
import os
import sys
import time
import uuid
from flask import Flask, request, jsonify, send_from_directory

# ============== 配置 ==============
BASE_URL = "https://dapi.guangyapan.com"
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def load_config():
    """从 config.json 读取凭证；不存在时给出提示"""
    if not os.path.exists(CONFIG_PATH):
        print(f"[错误] 配置文件不存在: {CONFIG_PATH}")
        print("请复制 config.example.json 为 config.json 并填入你的 client_id 和 client_secret")
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    return cfg.get("client_id", ""), cfg.get("client_secret", "")


CLIENT_ID, CLIENT_SECRET = load_config()

app = Flask(__name__, static_folder="static", static_url_path="")


# ============== 签名鉴权 ==============
def generate_sign(client_id, client_secret, nonce, timestamp):
    """
    sign = hex_lower( SHA512( MD5(srcStr) ) )
    注意: 先对 srcStr 做 MD5（得到 16 字节二进制），再对该二进制做 SHA512
    """
    src_str = (
        f"client_id={client_id}"
        f"&client_secret={client_secret}"
        f"&nonce={nonce}"
        f"&timestamp={timestamp}"
    )
    md5_bytes = hashlib.md5(src_str.encode("utf-8")).digest()
    return hashlib.sha512(md5_bytes).hexdigest()


def build_headers():
    nonce = uuid.uuid4().hex
    timestamp = str(int(time.time()))
    sign = generate_sign(CLIENT_ID, CLIENT_SECRET, nonce, timestamp)
    return {
        "Content-Type": "application/json",
        "client_id": CLIENT_ID,
        "nonce": nonce,
        "timestamp": timestamp,
        "sign": sign,
    }


def call_api(path, payload):
    """统一调用光压云盘 API"""
    import requests

    url = f"{BASE_URL}{path}"
    headers = build_headers()
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        return resp.json()
    except Exception as e:
        return {"code": -1, "msg": f"请求异常: {str(e)}", "data": None}


def is_success(data):
    code = data.get("code")
    if code is not None:
        return code == 0
    return data.get("msg") == "success"


# ============== 路由 ==============
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


# ---------- 3.3.1 获取文件列表 ----------
@app.route("/api/file/get_file_list", methods=["POST"])
def api_get_file_list():
    body = request.get_json(force=True)
    payload = {
        "parentId": body.get("parentId", ""),
        "page": body.get("page", 0),
        "pageSize": body.get("pageSize", 20),
        "orderBy": body.get("orderBy", 2),
        "sortType": body.get("sortType", 1),
    }
    if body.get("dirType") is not None:
        payload["dirType"] = body["dirType"]
    if body.get("fileTypes") is not None:
        payload["fileTypes"] = body["fileTypes"]
    if body.get("resType") is not None:
        payload["resType"] = body["resType"]
    if body.get("updated_after") is not None:
        payload["updated_after"] = body["updated_after"]
    return jsonify(call_api("/userres/v1/file/get_file_list", payload))


# ---------- 3.3.2 获取文件详情 ----------
@app.route("/api/file/get_file_detail", methods=["POST"])
def api_get_file_detail():
    body = request.get_json(force=True)
    payload = {"fileId": body.get("fileId", "")}
    return jsonify(call_api("/userres/v1/file/get_file_detail", payload))


# ---------- 3.3.3 文件/文件夹重命名 ----------
@app.route("/api/file/rename", methods=["POST"])
def api_rename():
    body = request.get_json(force=True)
    payload = {
        "fileId": body.get("fileId", ""),
        "newName": body.get("newName", ""),
    }
    return jsonify(call_api("/userres/v1/file/rename", payload))


# ---------- 3.3.4 预上传 ----------
@app.route("/api/developer/pre_upload", methods=["POST"])
def api_pre_upload():
    body = request.get_json(force=True)
    payload = {
        "token_id": body.get("token_id", ""),
        "file_ids": body.get("file_ids", []),
    }
    return jsonify(call_api("/developer/v1/pre_upload", payload))


# ---------- 3.3.5 预上传状态查询 ----------
@app.route("/api/developer/pre_upload_status", methods=["POST"])
def api_pre_upload_status():
    body = request.get_json(force=True)
    payload = {"task_id": body.get("task_id", "")}
    return jsonify(call_api("/developer/v1/pre_upload_status", payload))


# ---------- 3.3.6 预上传详情获取 ----------
@app.route("/api/developer/pre_upload_detail", methods=["POST"])
def api_pre_upload_detail():
    body = request.get_json(force=True)
    payload = {
        "task_id": body.get("task_id", ""),
        "page": body.get("page", 1),
        "page_size": body.get("page_size", 20),
    }
    if body.get("filter"):
        payload["filter"] = body["filter"]
    return jsonify(call_api("/developer/v1/pre_upload_detail", payload))


# ---------- 3.3.7 通过文件ID上传 ----------
@app.route("/api/developer/upload_by_fileid", methods=["POST"])
def api_upload_by_fileid():
    body = request.get_json(force=True)
    payload = {
        "token_id": body.get("token_id", ""),
        "file_ids": body.get("file_ids", []),
    }
    if body.get("duplicate_name_policy") is not None:
        payload["duplicate_name_policy"] = body["duplicate_name_policy"]
    return jsonify(call_api("/developer/v1/upload_by_fileid", payload))


# ---------- 3.3.8 上传状态查询 ----------
@app.route("/api/developer/upload_status", methods=["POST"])
def api_upload_status():
    body = request.get_json(force=True)
    payload = {"task_id": body.get("task_id", "")}
    return jsonify(call_api("/developer/v1/upload_status", payload))


# ---------- 3.3.9 上传跳过的文件列表 ----------
@app.route("/api/developer/upload_skipped_list", methods=["POST"])
def api_upload_skipped_list():
    body = request.get_json(force=True)
    payload = {
        "task_id": body.get("task_id", ""),
        "page_size": body.get("page_size", 100),
    }
    if body.get("reason"):
        payload["reason"] = body["reason"]
    if body.get("cursor"):
        payload["cursor"] = body["cursor"]
    return jsonify(call_api("/developer/v1/upload_skipped_list", payload))


# ---------- 3.3.10 上传成功的文件列表 ----------
@app.route("/api/developer/upload_success_list", methods=["POST"])
def api_upload_success_list():
    body = request.get_json(force=True)
    payload = {
        "task_id": body.get("task_id", ""),
        "page_size": body.get("page_size", 100),
    }
    if body.get("cursor"):
        payload["cursor"] = body["cursor"]
    return jsonify(call_api("/developer/v1/upload_success_list", payload))


if __name__ == "__main__":
    print("=" * 50)
    print("光压云盘开发者 API 服务启动")
    print("访问地址: http://localhost:5001")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5001, debug=True)
