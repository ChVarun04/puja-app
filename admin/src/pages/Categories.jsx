import { useEffect, useState } from "react";
import { Table, Button, Modal, Form, Input, Select, Switch, message } from "antd";
import api from "../api";

export default function Categories() {
  const [rows, setRows] = useState([]);
  const [deities, setDeities] = useState([]);
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form] = Form.useForm();

  const load = () => api.get("/admin/puja-categories").then((r) => setRows(r.data));
  useEffect(() => {
    load();
    api.get("/admin/deities").then((r) => setDeities(r.data));
  }, []);

  const deityName = (id) => deities.find((d) => d.id === id)?.name || "-";

  const openModal = (row) => {
    setEditing(row);
    form.resetFields();
    form.setFieldsValue(row || { is_active: true });
    setOpen(true);
  };

  const save = async () => {
    const values = await form.validateFields();
    try {
      if (editing) await api.put(`/admin/puja-categories/${editing.id}`, values);
      else await api.post("/admin/puja-categories", values);
      message.success("Saved");
      setOpen(false);
      load();
    } catch (e) {
      message.error(e.response?.data?.detail || "Save failed");
    }
  };

  return (
    <>
      <Button type="primary" onClick={() => openModal(null)} style={{ marginBottom: 16 }}>Add Puja Category</Button>
      <Table rowKey="id" dataSource={rows} columns={[
        { title: "ID", dataIndex: "id", width: 70 },
        { title: "Name", dataIndex: "name" },
        { title: "Deity", dataIndex: "deity_id", render: deityName },
        { title: "Description", dataIndex: "description" },
        { title: "Active", dataIndex: "is_active", render: (v) => (v ? "Yes" : "No") },
        { title: "", render: (_, r) => <Button onClick={() => openModal(r)}>Edit</Button> },
      ]} />
      <Modal title={editing ? "Edit Category" : "Add Category"} open={open} onOk={save} onCancel={() => setOpen(false)}>
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="Name" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="deity_id" label="Deity (optional)">
            <Select allowClear options={deities.map((d) => ({ value: d.id, label: d.name }))} />
          </Form.Item>
          <Form.Item name="description" label="Description"><Input.TextArea rows={2} /></Form.Item>
          <Form.Item name="instructions" label="Puja Instructions"><Input.TextArea rows={3} /></Form.Item>
          <Form.Item name="is_active" label="Active" valuePropName="checked"><Switch /></Form.Item>
        </Form>
      </Modal>
    </>
  );
}