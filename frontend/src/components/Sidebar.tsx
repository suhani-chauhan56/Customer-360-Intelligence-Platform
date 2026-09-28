import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  UserCheck,
  Users,
  TrendingUp,
  AlertTriangle,
  Smile,
  Compass,
  BarChart3,
  Search,
  ShieldCheck,
  Bot,
  BookOpen,
  ChevronLeft,
  ChevronRight,
  Database,
  Layers,
} from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

interface SidebarProps {
  collapsed: boolean;
  setCollapsed: (collapsed: boolean) => void;
}

interface NavItem {
  name: string;
  path: string;
  icon: React.ElementType;
  badge?: string;
  badgeColor?: string;
}

interface NavSection {
  title: string;
  items: NavItem[];
}

export const Sidebar: React.FC<SidebarProps> = ({ collapsed, setCollapsed }) => {
  const location = useLocation();
  const { theme } = useTheme();

  const sections: NavSection[] = [
    {
      title: 'CORE INTELLIGENCE',
      items: [
        { name: 'Executive Overview', path: '/', icon: LayoutDashboard },
        { name: 'Customer 360', path: '/customer-360', icon: UserCheck, badge: '94k' },
        { name: 'Customer Segmentation', path: '/segmentation', icon: Users },
        { name: 'Customer Value / CLV', path: '/clv', icon: TrendingUp },
      ],
    },
    {
      title: 'PREDICTIVE & RISK AI',
      items: [
        { name: 'Churn Intelligence', path: '/churn', icon: AlertTriangle, badge: 'ML' },
        { name: 'Sentiment & CSAT', path: '/sentiment', icon: Smile },
        { name: 'Recommendations', path: '/recommendations', icon: Compass },
      ],
    },
    {
      title: 'EXPLORATION & HUB',
      items: [
        { name: 'Revenue & Products', path: '/revenue-products', icon: BarChart3 },
        { name: 'Analytics Explorer', path: '/explorer', icon: Search },
        { name: 'Data Quality & Lineage', path: '/data-quality', icon: ShieldCheck, badge: '100%' },
      ],
    },
    {
      title: 'DECISION SUPPORT',
      items: [
        { name: 'Ask CustomerAtlas AI', path: '/ask-atlas', icon: Bot, badge: 'Grounded' },
        { name: 'Methodology & Standards', path: '/methodology', icon: BookOpen },
      ],
    },
  ];

  return (
    <aside
      className={`fixed top-0 left-0 z-30 h-screen transition-all duration-300 flex flex-col border-r bg-white dark:bg-surface-900 border-surface-200 dark:border-surface-800 ${
        collapsed ? 'w-20' : 'w-64'
      }`}
    >
      {/* Brand Header */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-surface-200 dark:border-surface-800">
        <div className="flex items-center space-x-3 overflow-hidden">
          <div className="h-9 w-9 rounded-xl bg-brand-600 flex items-center justify-center text-white shadow-md shadow-brand-500/20 shrink-0">
            <Compass className="h-5 w-5 animate-pulse" />
          </div>
          {!collapsed && (
            <div className="flex flex-col">
              <span className="font-bold text-base tracking-tight text-surface-900 dark:text-white flex items-center gap-1.5">
                CustomerAtlas <span className="text-[10px] uppercase font-extrabold px-1.5 py-0.5 rounded bg-brand-100 dark:bg-brand-950/80 text-brand-700 dark:text-brand-300">AI</span>
              </span>
              <span className="text-[11px] text-surface-500 dark:text-surface-400 font-medium">Customer 360 Platform</span>
            </div>
          )}
        </div>

        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1.5 rounded-lg text-surface-400 hover:text-surface-700 dark:hover:text-surface-200 hover:bg-surface-100 dark:hover:bg-surface-800 transition-colors"
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </button>
      </div>

      {/* Navigation Links */}
      <div className="flex-1 overflow-y-auto py-4 px-3 space-y-6">
        {sections.map((section, idx) => (
          <div key={idx} className="space-y-1">
            {!collapsed && (
              <h4 className="text-[10px] font-bold uppercase tracking-wider text-surface-400 dark:text-surface-500 px-3 mb-2">
                {section.title}
              </h4>
            )}
            {section.items.map(item => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;

              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all group relative ${
                    isActive
                      ? 'bg-brand-50 dark:bg-brand-950/50 text-brand-600 dark:text-brand-400 shadow-sm border border-brand-200/50 dark:border-brand-800/40'
                      : 'text-surface-600 dark:text-surface-400 hover:text-surface-900 dark:hover:text-surface-100 hover:bg-surface-100/70 dark:hover:bg-surface-800/50'
                  }`}
                  title={collapsed ? item.name : undefined}
                >
                  <Icon
                    className={`h-4 w-4 shrink-0 transition-transform duration-200 group-hover:scale-110 ${
                      isActive ? 'text-brand-600 dark:text-brand-400' : 'text-surface-400 dark:text-surface-500'
                    }`}
                  />
                  {!collapsed && (
                    <span className="truncate flex-1">{item.name}</span>
                  )}
                  {!collapsed && item.badge && (
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-surface-100 dark:bg-surface-800 text-surface-600 dark:text-surface-300 border border-surface-200 dark:border-surface-700">
                      {item.badge}
                    </span>
                  )}
                </NavLink>
              );
            })}
          </div>
        ))}
      </div>

      {/* System Health Badge at Bottom */}
      <div className="p-3 border-t border-surface-200 dark:border-surface-800">
        {!collapsed ? (
          <div className="flex items-center justify-between p-2.5 rounded-xl bg-surface-50 dark:bg-surface-800/60 border border-surface-200 dark:border-surface-700/50">
            <div className="flex items-center gap-2">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <div className="flex flex-col">
                <span className="text-[11px] font-semibold text-surface-700 dark:text-surface-200">System Healthy</span>
                <span className="text-[10px] text-surface-400">94,983 Profiles Loaded</span>
              </div>
            </div>
            <Database className="h-4 w-4 text-surface-400" />
          </div>
        ) : (
          <div className="flex justify-center" title="System Healthy: 94,983 profiles loaded">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
            </span>
          </div>
        )}
      </div>
    </aside>
  );
};
