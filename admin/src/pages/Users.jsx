import { useEffect, useState } from "react";
import { Table, Input, Switch, Tag, message } from "antd";
import api from "../api";

export default function Users() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState("");

  const load = (q = search) => {
    setLoading(true);
    api.get("/admin/users", { params: { search: q || undefined, skip: 0, limit: 200 } })
      .then((r) => setRows(r.data))
      .catch(() => message.error("Could not load users"))
      .finally(() => setLoading(false));
  };
  useEffect(() => { load(""); }, []);

  const toggle = async (user, checked) => {
    try {
      await api.patch(`/admin/users/${user.id}/status`, null, { params: { is_active: checked } });
      message.success(checked ? "User activated" : "User deactivated");
      load();
    } catch (e) {
      message.error(e.response?.data?.detail || "Update failed");
    }
  };

  return (
    <>
      <Input.Search
        placeholder="Search by name, email or mobile"
        allowClear
        onSearch={(v) => { setSearch(v); load(v); }}
        style={{ maxWidth: 360, marginBottom: 16 }}
      />
      <Table rowKey="id" loading={loading} dataSource={rows} columns={[
        { title: "ID", dataIndex: "id", width: 70 },
        { title: "Name", dataIndex: "name" },
        { title: "Email", dataIndex: "email" },
        { title: "Mobile", dataIndex: "mobile" },
        { title: "Status", dataIndex: "is_active", render: (v) => <Tag color={v ? "green" : "red"}>{v ? "Active" : "Inactive"}</Tag> },
        { title: "Active", render: (_, r) => <Switch checked={r.is_active} onChange={(c) => toggle(r, c)} /> },
      ]} />
    </>
  );
}