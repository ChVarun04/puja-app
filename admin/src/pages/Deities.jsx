import { useEffect, useState } from "react";
import { Table, Button, Modal, Form, Input, Switch, Space, message } from "antd";
import api from "../api";

export default function Deities() {
  const [rows, setRows] = useState([]);
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form] = Form.useForm();

  const load = () => api.get("/admin/deities").then((r) => setRows(r.data));
  useEffect(() => { load(); }, []);

  const openModal = (row) => {
    setEditing(row);
    form.resetFields();
    form.setFieldsValue(row || { is_active: true });
    setOpen(true);
  };

  const save = async () => {
    const values = await form.validateFields();
    try {
      if (editing) await api.put(`/admin/deities/${editing.id}`, values);
      else await api.post("/admin/deities", values);
      message.success("Saved");
      setOpen(false);
      load();
    } catch (e) {
      message.error(e.response?.data?.detail || "Save failed");
    }
  };

  return (
    <>
      <Button type="primary" onClick={() => openModal(null)} style={{ marginBottom: 16 }}>Add Deity</Button>
      <Table rowKey="id" dataSource={rows} columns={[
        { title: "ID", dataIndex: "id", width: 70 },
        { title: "Name", dataIndex: "name" },
        { title: "Description", dataIndex: "description" },
        { title: "Active", dataIndex: "is_active", render: (v) => (v ? "Yes" : "No") },
        { title: "", render: (_, r) => <Button onClick={() => openModal(r)}>Edit</Button> },
      ]} />
      <Modal title={editing ? "Edit Deity" : "Add Deity"} open={open} onOk={save} onCancel={() => setOpen(false)}>
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="Name" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="description" label="Description"><Input.TextArea rows={3} /></Form.Item>
          <Form.Item name="is_active" label="Active" valuePropName="checked"><Switch /></Form.Item>
        </Form>
      </Modal>
    </>
  );
}