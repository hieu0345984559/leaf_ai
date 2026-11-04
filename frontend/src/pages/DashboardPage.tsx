import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Activity,
  AlertTriangle,
  CheckCircle,
  Scan,
  TrendingUp,
  Clock,
  ArrowRight,
  Sparkles,
  ShieldCheck,
  Layers,
  Cpu
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts';
import { apiGetDashboardStats } from '../api/dashboard';
import { resolveMediaUrl } from '../api/client';
import { StatCard } from '../components/StatCard';
import { LoadingState } from '../components/LoadingState';
import { EmptyState } from '../components/EmptyState';
import type { DashboardStats } from '../types';

const CHART_PALETTE = ['#15803D', '#059669', '#0D9488', '#047857', '#D97706', '#B45309'];

export function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    apiGetDashboardStats()
      .then(setStats)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <LoadingState message="Đang tải dữ liệu thống kê chẩn đoán..." />;
  }

  if (!stats) {
    return (
      <EmptyState
        title="Không thể tải số liệu thống kê"
        description="Không thể kết nối đến máy chủ chẩn đoán thị giác."
      />
    );
  }

  // Format chart data
  const chartData = Object.entries(stats.disease_distribution).map(([rawName, count]) => {
    const cleanName = rawName.replace('Tomato___', '').replace(/_/g, ' ');
    return {
      name: cleanName,
      count,
    };
  });

  return (
    <div className="space-y-8 sm:space-y-10">
      {/* Hero Banner Section */}
      <div className="clean-card p-8 sm:p-10 lg:p-12 rounded-3xl bg-gradient-to-br from-white/95 via-white/90 to-[#F0FDF4]/90 border border-[#E2EFE7] relative overflow-hidden shadow-xs">
        {/* Subtle decorative background organic glow */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-100/40 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20" />
        <div className="absolute bottom-0 right-1/3 w-80 h-80 bg-amber-100/30 rounded-full blur-2xl pointer-events-none -mb-20" />

        <div className="max-w-3xl relative z-10 space-y-5 sm:space-y-6">
          {/* Top Pill Badge */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#F0FDF4] border border-emerald-200/80 text-xs font-bold text-[#15803D] shadow-2xs">
            <Sparkles size={14} className="text-amber-500" />
            <span>Nhận Diện Bệnh Hại Lá Chè Bằng AI Theo Thời Gian Thực (Camellia sinensis)</span>
          </div>

          {/* Main Headline */}
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-[#0F172A] tracking-tight leading-[1.18] font-['Space_Grotesk']">
            Chẩn đoán bệnh học lá & <span className="text-gradient">bảo vệ vùng trồng chè</span>
          </h1>

          {/* Subtitle */}
          <p className="text-sm sm:text-base text-slate-600 leading-relaxed max-w-2xl">
            LEAF_AI nhận diện các bệnh hại lá chè (Camellia sinensis), khoanh vùng tổn thương chính xác với mô hình YOLO và xây dựng lộ trình điều trị toàn diện.
          </p>

          {/* Action Buttons */}
          <div className="pt-2 flex flex-wrap items-center gap-3.5">
            <button
              onClick={() => navigate('/diagnose')}
              className="btn-primary py-3 px-6 text-sm"
            >
              <Scan size={17} />
              <span>Bắt Đầu Chẩn Đoán Lá</span>
              <ArrowRight size={15} />
            </button>

            <button
              onClick={() => navigate('/diseases')}
              className="btn-secondary py-3 px-5 text-sm"
            >
              <span>Khám Phá Thư Viện Bệnh</span>
            </button>
          </div>

          {/* Micro Trust Indicators */}
          <div className="pt-2 flex flex-wrap items-center gap-6 sm:gap-8 text-xs text-slate-500 font-medium">
            <span className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-600" />
              YOLOv11 Thị Giác Sâu
            </span>
            <span className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-teal-600" />
              6 Tác Nhân Bệnh Hại Chè
            </span>
            <span className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-amber-500" />
              Phác Đồ Canh Tác Chuẩn
            </span>
          </div>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
        <StatCard
          title="Tổng Lượt Quét"
          value={stats.total_diagnoses}
          subtitle="Tổng số lần suy luận thị giác đã thực hiện"
          icon={<Activity size={22} />}
          variant="forest"
        />

        <StatCard
          title="Vùng Bệnh Được Phát Hiện"
          value={stats.detected_count}
          subtitle="Các vị trí tổn thương cần can thiệp nông học"
          icon={<AlertTriangle size={22} />}
          variant="amber"
        />

        <StatCard
          title="Lá Chè Khỏe Mạnh"
          value={stats.no_detection_count}
          subtitle="Mẫu lá sạch bệnh, không có đốm tổn thương"
          icon={<CheckCircle size={22} />}
          variant="emerald"
        />
      </div>

      {/* Analytics Chart & Recent Activity Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 sm:gap-8">
        {/* Chart Column (7 cols) */}
        <div className="lg:col-span-7 clean-card p-6 sm:p-8 rounded-3xl space-y-6 flex flex-col justify-between shadow-xs">
          <div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-[#F0FDF4] text-[#15803D] border border-emerald-200/60">
                  <TrendingUp size={19} />
                </div>
                <div>
                  <h3 className="text-base font-bold text-[#0F172A] font-['Space_Grotesk']">
                    Phân Bố Bệnh Hại Phát Hiện
                  </h3>
                  <p className="text-xs text-slate-500">Tần suất xuất hiện trên các mẫu lá đã chẩn đoán</p>
                </div>
              </div>
              <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-100 text-slate-600 font-mono">
                {chartData.length} nhóm bệnh
              </span>
            </div>

            {chartData.length > 0 ? (
              <div className="h-72 sm:h-80 w-full pt-6">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 15, right: 15, left: -20, bottom: 30 }}>
                    <XAxis
                      dataKey="name"
                      tick={{ fill: '#64748B', fontSize: 11 }}
                      interval={0}
                      angle={-20}
                      textAnchor="end"
                    />
                    <YAxis
                      tick={{ fill: '#64748B', fontSize: 11 }}
                      allowDecimals={false}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#FFFFFF',
                        borderColor: '#E2EFE7',
                        borderRadius: '12px',
                        boxShadow: '0 8px 20px -4px rgba(15, 23, 42, 0.1)',
                        color: '#0F172A',
                        fontSize: '12px',
                        fontWeight: 600,
                        padding: '8px 12px',
                      }}
                    />
                    <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                      {chartData.map((_, i) => (
                        <Cell key={i} fill={CHART_PALETTE[i % CHART_PALETTE.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="py-16 text-center text-xs text-slate-400">
                Chưa ghi nhận bệnh hại nào. Hãy thực hiện lượt quét đầu tiên để trực quan hóa dữ liệu.
              </div>
            )}
          </div>
        </div>

        {/* Recent Diagnoses Column (5 cols) */}
        <div className="lg:col-span-5 clean-card p-6 sm:p-8 rounded-3xl space-y-6 flex flex-col justify-between shadow-xs">
          <div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-emerald-50 text-[#15803D] border border-emerald-200/60">
                  <Clock size={19} />
                </div>
                <div>
                  <h3 className="text-base font-bold text-[#0F172A] font-['Space_Grotesk']">Lượt Quét Gần Đây</h3>
                  <p className="text-xs text-slate-500">Các bản ghi kiểm tra lá chè mới nhất</p>
                </div>
              </div>
              <button
                onClick={() => navigate('/history')}
                className="text-xs font-bold text-[#15803D] hover:text-[#166534] cursor-pointer flex items-center gap-1"
              >
                <span>Xem Tất Cả</span>
                <ArrowRight size={13} />
              </button>
            </div>

            <div className="space-y-3 pt-5">
              {stats.recent_diagnoses.length > 0 ? (
                stats.recent_diagnoses.map((item) => {
                  const dateStr = item.created_at
                    ? new Date(item.created_at).toLocaleDateString('vi-VN')
                    : '';
                  const cleanPrimary = item.primary_disease
                    ? item.primary_disease.replace('Tomato___', '').replace(/_/g, ' ')
                    : item.status === 'detected'
                    ? 'Đã Phát Hiện Bệnh'
                    : 'Lá Khỏe Mạnh / Không Có Bệnh';

                  return (
                    <div
                      key={item.id}
                      onClick={() => navigate('/history')}
                      className="p-3.5 rounded-2xl bg-white/60 hover:bg-[#F0FDF4] border border-[#E2EFE7] hover:border-emerald-200/80 flex items-center gap-3.5 transition-all cursor-pointer group"
                    >
                      <img
                        src={resolveMediaUrl(item.original_image_url)}
                        alt="Ảnh Thu Nhỏ Lá Chè"
                        className="w-13 h-13 sm:w-14 sm:h-14 rounded-xl object-cover bg-slate-100 border border-[#E2EFE7] shrink-0"
                      />

                      <div className="min-w-0 flex-1">
                        <p className="text-xs sm:text-sm font-bold text-slate-900 group-hover:text-[#15803D] transition-colors truncate font-['DM_Sans']">
                          {cleanPrimary}
                        </p>
                        <p className="text-[11px] text-slate-500 font-mono mt-0.5">
                          {dateStr} • {item.detection_count} điểm bệnh
                        </p>
                      </div>

                      <span
                        className={`text-[10px] font-bold px-2.5 py-1 rounded-full shrink-0 font-mono ${
                          item.status === 'detected'
                            ? 'bg-amber-50 text-amber-800 border border-amber-200'
                            : 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                        }`}
                      >
                        {item.status === 'detected' ? 'Có Bệnh' : 'Khỏe Mạnh'}
                      </span>
                    </div>
                  );
                })
              ) : (
                <div className="py-16 text-center text-xs text-slate-400">
                  Chưa có lượt quét chẩn đoán nào gần đây.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Feature Capabilities Footer Strip */}
      <div className="clean-card p-6 sm:p-8 rounded-3xl shadow-2xs">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-6 text-center">
          <div className="flex flex-col items-center gap-2 p-2">
            <div className="w-11 h-11 rounded-xl bg-[#F0FDF4] text-[#15803D] border border-emerald-200/80 flex items-center justify-center">
              <Cpu size={20} />
            </div>
            <span className="text-xs sm:text-sm font-bold text-slate-900 font-['Space_Grotesk']">Ultralytics YOLOv11</span>
            <span className="text-[11px] text-slate-500">Thị Giác Học Sâu Tăng Tốc</span>
          </div>
          <div className="flex flex-col items-center gap-2 p-2">
            <div className="w-11 h-11 rounded-xl bg-teal-50 text-teal-700 border border-teal-200 flex items-center justify-center">
              <Layers size={20} />
            </div>
            <span className="text-xs sm:text-sm font-bold text-slate-900 font-['Space_Grotesk']">6 Nhóm Bệnh Lá Chè</span>
            <span className="text-[11px] text-slate-500">Tác Nhân Bệnh Chè (Camellia sinensis)</span>
          </div>
          <div className="flex flex-col items-center gap-2 p-2">
            <div className="w-11 h-11 rounded-xl bg-amber-50 text-amber-700 border border-amber-200 flex items-center justify-center">
              <Scan size={20} />
            </div>
            <span className="text-xs sm:text-sm font-bold text-slate-900 font-['Space_Grotesk']">Hộp Định Vị Đa Điểm</span>
            <span className="text-[11px] text-slate-500">Chính Xác Từng Pixel</span>
          </div>
          <div className="flex flex-col items-center gap-2 p-2">
            <div className="w-11 h-11 rounded-xl bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center justify-center">
              <ShieldCheck size={20} />
            </div>
            <span className="text-xs sm:text-sm font-bold text-slate-900 font-['Space_Grotesk']">Phác Đồ Quản Lý IPM</span>
            <span className="text-[11px] text-slate-500">Hướng Dẫn Nông Học Chuyên Sâu</span>
          </div>
        </div>
      </div>
    </div>
  );
}
