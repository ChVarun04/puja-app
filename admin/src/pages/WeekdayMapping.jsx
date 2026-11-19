import { useEffect, useState } from "react";
import { Table, Select, Tag, Alert, message } from "antd";
import api from "../api";

const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
// JS getDay(): Sunday=0. Backend: Monday=0.
const todayIndex = (new Date().getDay() + 6) % 7;

export default function WeekdayMapping() {
  const [rows, setRows] = useState([]);
  const [deities, setDeities] = useState([]);
  const [saving, setSaving] = useState(null);

  const load = () => api.get("/admin/weekday-mappings").then((r) => setRows(r.data));
  useEffect(() => {
    load();
    api.get("/admin/deities").then((r) => setDeities(r.data));
  }, []);

  const change = async (weekday, deity_id) => {
    setSaving(weekday);
    try {
      await api.put("/admin/weekday-mappings", { weekday, deity_id });
      message.success(`${DAYS[weekday]} updated`);
      await load();
    } catch (e) {
      message.error(e.response?.data?.detail || "Update failed");
    } finally {
      setSaving(null);
    }
  };

  return (
    <>
      <Alert
        type="info" showIcon style={{ marginBottom: 16 }}
        message="The deity chosen here is shown to users on their dashboard for that weekday. Changes apply immediately."
      />
      <Table rowKey="weekday" pagination={false} dataSource={rows} columns={[
        {
          title: "Day", dataIndex: "weekday",
          render: (v) => <>{DAYS[v]} {v === todayIndex && <Tag color="orange">Today</Tag>}</>,
        },
        {
          title: "Deity", dataIndex: "deity_id",
          render: (v, r) => (
            <Select
              style={{ width: 280 }}
              value={v}
              loading={saving === r.weekday}
              onChange={(id) => change(r.weekday, id)}
              options={deities.map((d) => ({ value: d.id, label: d.name }))}
            />
          ),
        },
      ]} />
    </>
  );
}