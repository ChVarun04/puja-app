import { useEffect, useState } from "react";
import { Row, Col, Card, Statistic, List, Spin, message } from "antd";
import api from "../api";

export default function Dashboard() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    api.get("/admin/stats")
      .then((res) => setStats(res.data))
      .catch(() => message.error("Could not load stats"));
  }, []);

  if (!stats) return <Spin size="large" />;

  return (
    <>
      <Row gutter={16}>
        <Col span={6}><Card><Statistic title="Total Users" value={stats.users} /></Card></Col>
        <Col span={6}><Card><Statistic title="Audio Files" value={stats.audio} /></Card></Col>
        <Col span={6}><Card><Statistic title="Video Files" value={stats.video} /></Card></Col>
        <Col span={6}><Card><Statistic title="Puja Categories" value={stats.categories} /></Card></Col>
      </Row>
      <Card title="Recent Uploads" style={{ marginTop: 24 }}>
        <List
          dataSource={stats.recent}
          locale={{ emptyText: "No uploads yet" }}
          renderItem={(m) => <List.Item>#{m.id} · {m.title}</List.Item>}
        />
      </Card>
    </>
  );
}