import { Layout, Menu, Button } from "antd";
import {
  DashboardOutlined, CustomerServiceOutlined, AppstoreOutlined,
  StarOutlined, TeamOutlined, CalendarOutlined,
} from "@ant-design/icons";
import { Outlet, useNavigate, useLocation } from "react-router-dom";

const { Sider, Header, Content } = Layout;

const items = [
  { key: "/", icon: <DashboardOutlined />, label: "Dashboard" },
  { key: "/users", icon: <TeamOutlined />, label: "Users" },
  { key: "/media", icon: <CustomerServiceOutlined />, label: "Media" },
  { key: "/deities", icon: <StarOutlined />, label: "Deities" },
  { key: "/categories", icon: <AppstoreOutlined />, label: "Puja Categories" },
  { key: "/weekdays", icon: <CalendarOutlined />, label: "Weekday Mapping" },
];

export default function AdminLayout() {
  const navigate = useNavigate();
  const location = useLocation();

  const logout = () => {
    localStorage.removeItem("admin_token");
    navigate("/login");
  };

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider theme="light" width={220}>
        <div style={{ padding: 16, fontWeight: 700, fontSize: 18, color: "#d9730d" }}>Puja Admin</div>
        <Menu mode="inline" selectedKeys={[location.pathname]} items={items} onClick={(e) => navigate(e.key)} />
      </Sider>
      <Layout>
        <Header style={{ background: "#fff", display: "flex", justifyContent: "flex-end", alignItems: "center" }}>
          <Button onClick={logout}>Logout</Button>
        </Header>
        <Content style={{ margin: 24 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}