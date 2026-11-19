import { useEffect, useState } from "react";
import { Table, Button, Modal, Form, Input, Select, Upload, Popconfirm, Tag, Space, message } from "antd";
import { UploadOutlined } from "@ant-design/icons";
import api from "../api";

const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
  .map((d, i) => ({ value: i, label: d }));

export default function Media() {
  const [rows, setRows] = useState([]);
  const [deities, setDeities] = useState([]);
  const [cats, setCats] = useState([]);
  const [users, setUsers] = useState([]);
  const [uploadOpen, setUploadOpen] = useState(false);
  const [assignFor, setAssignFor] = useState(null);
  const [assignUser, setAssignUser] = useState(null);
  const [fileList, setFileList] = useState([]);
  const [saving, setSaving] = useState(false);
  const [form] = Form.useForm();

  const load = () => api.get("/admin/media").then((r) => setRows(r.data));
  useEffect(() => {
    load();
    api.get("/admin/deities").then((r) => setDeities(r.data));
    api.get("/admin/puja-categories").then((r) => setCats(r.data));
    api.get("/admin/users").then((r) => setUsers(r.data));
  }, []);

  const upload = async () => {
    const v = await form.validateFields();
    if (!fileList.length) return message.error("Choose a file");
    const fd = new FormData();
    fd.append("title", v.title);
    fd.append("content_type", v.content_type);
    fd.append("access_type", v.access_type);
    fd.append("status", v.status);
    ["description", "language", "deity_id", "puja_category_id", "weekday"].forEach((k) => {
      if (v[k] !== undefined && v[k] !== null && v[k] !== "") fd.append(k, v[k]);
    });
    fd.append("file", fileList[0].originFileObj);
    setSaving(true);
    try {
      await api.post("/admin/media", fd);
      message.success("Uploaded");
      setUploadOpen(false);
      form.resetFields();
      setFileList([]);
      load();
    } catch (e) {
      message.error(e.response?.data?.detail || "Upload failed");
    } finally {
      setSaving(false);
    }
  };

  const assign = async () => {
    if (!assignUser) return message.error("Select a user");
    try {
      await api.post(`/admin/media/${assignFor.id}/assign/${assignUser}`);
      message.success("Assigned");
      setAssignFor(null);
      setAssignUser(null);
    } catch (e) {
      message.error(e.response?.data?.detail || "Assign failed");
    }
  };

  const remove = async (id) => {
    await api.delete(`/admin/media/${id}`);
    message.success("Deleted");
    load();
  };

  const userLabel = (u) => `${u.full_name || u.name || ""} (${u.email}) #${u.id}`;

  return (
    <>
      <Button type="primary" icon={<UploadOutlined />} onClick={() => setUploadOpen(true)} style={{ marginBottom: 16 }}>
        Upload Media
      </Button>
      <Table rowKey="id" dataSource={rows} columns={[
        { title: "ID", dataIndex: "id", width: 60 },
        { title: "Title", dataIndex: "title" },
        { title: "Type", dataIndex: "content_type" },
        { title: "Weekday", dataIndex: "weekday", render: (v) => (v == null ? "-" : DAYS[v].label) },
        { title: "Access", dataIndex: "access_type", render: (v) => <Tag color={v === "common" ? "green" : "orange"}>{v}</Tag> },
        { title: "Status", dataIndex: "status" },
        {
          title: "Actions",
          render: (_, r) => (
            <Space>
              {r.access_type === "user_specific" && <Button onClick={() => setAssignFor(r)}>Assign to user</Button>}
              <Popconfirm title="Delete this media?" onConfirm={() => remove(r.id)}>
                <Button danger>Delete</Button>
              </Popconfirm>
            </Space>
          ),
        },
      ]} />

      <Modal title="Upload Media" open={uploadOpen} onOk={upload} confirmLoading={saving}
        onCancel={() => setUploadOpen(false)} okText="Upload">
        <Form form={form} layout="vertical" initialValues={{ content_type: "audio", access_type: "common", status: "active" }}>
          <Form.Item name="title" label="Title" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="content_type" label="Type">
            <Select options={[{ value: "audio", label: "Audio" }, { value: "video", label: "Video" }]} />
          </Form.Item>
          <Form.Item name="description" label="Description"><Input.TextArea rows={2} /></Form.Item>
          <Form.Item name="language" label="Language"><Input placeholder="e.g. Telugu" /></Form.Item>
          <Form.Item name="deity_id" label="Deity">
            <Select allowClear options={deities.map((d) => ({ value: d.id, label: d.name }))} />
          </Form.Item>
          <Form.Item name="puja_category_id" label="Puja Category">
            <Select allowClear options={cats.map((c) => ({ value: c.id, label: c.name }))} />
          </Form.Item>
          <Form.Item name="weekday" label="Weekday (optional)"><Select allowClear options={DAYS} /></Form.Item>
          <Form.Item name="access_type" label="Access">
            <Select options={[
              { value: "common", label: "Common (all users)" },
              { value: "user_specific", label: "User-specific (assign to users)" },
            ]} />
          </Form.Item>
          <Form.Item name="status" label="Status">
            <Select options={[{ value: "draft", label: "Draft" }, { value: "active", label: "Active" }, { value: "inactive", label: "Inactive" }]} />
          </Form.Item>
          <Form.Item label="File" required>
            <Upload beforeUpload={() => false} maxCount={1} fileList={fileList} onChange={(e) => setFileList(e.fileList)}>
              <Button icon={<UploadOutlined />}>Select file</Button>
            </Upload>
          </Form.Item>
        </Form>
      </Modal>

      <Modal title={`Assign "${assignFor?.title}" to a user`} open={!!assignFor} onOk={assign}
        onCancel={() => setAssignFor(null)} okText="Assign">
        <Select style={{ width: "100%" }} showSearch optionFilterProp="label" placeholder="Select user"
          value={assignUser} onChange={setAssignUser}
          options={users.map((u) => ({ value: u.id, label: userLabel(u) }))} />
      </Modal>
    </>
  );
}