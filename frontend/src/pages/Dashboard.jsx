import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
    ArrowLeft,
    FileText,
    CheckCircle,
    AlertCircle,
    Clock,
    Download,
    Activity
} from 'lucide-react'

const StatCard = ({ title, value, icon: Icon, color, delay }) => (
    <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay }}
        className="glass-card stat-card"
        style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '0.5rem',
            padding: '1.5rem',
            background: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid rgba(255,255,255,0.1)'
        }}
    >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{title}</span>
            <div style={{
                padding: '8px',
                borderRadius: '8px',
                background: `rgba(${color}, 0.1)`,
                color: `rgb(${color})`
            }}>
                <Icon size={20} />
            </div>
        </div>
        <span style={{ fontSize: '2rem', fontWeight: 700, color: 'white' }}>{value}</span>
    </motion.div>
)

const Dashboard = () => {
    const [metrics, setMetrics] = useState({
        totalUploads: 0,
        successRate: 0,
        totalLinesProcessed: 0,
        failedUploads: 0,
        todayUploads: 0
    })
    const [recentUploads, setRecentUploads] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [metricsRes, uploadsRes] = await Promise.all([
                    fetch('https://172.16.10.130:8000/dashboard/metrics'),
                    fetch('https://172.16.10.130:8000/dashboard/recent-uploads')
                ])

                if (metricsRes.ok && uploadsRes.ok) {
                    const metricsData = await metricsRes.json()
                    const uploadsData = await uploadsRes.json()
                    setMetrics(metricsData)
                    setRecentUploads(uploadsData)
                }
            } catch (error) {
                console.error("Failed to fetch dashboard data", error)
            } finally {
                setLoading(false)
            }
        }

        fetchData()
        // Poll every 30 seconds for live updates
        const interval = setInterval(fetchData, 30000)
        return () => clearInterval(interval)
    }, [])

    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: { staggerChildren: 0.1 }
        }
    }

    return (
        <div className="app-container" style={{
            maxWidth: '1200px',
            margin: '0 auto',
            padding: '2rem',
            display: 'flex',
            flexDirection: 'column'
        }}>
            <div style={{ marginBottom: '2rem' }}>
                <Link to="/" style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    color: 'var(--text-secondary)',
                    textDecoration: 'none',
                    marginBottom: '1rem',
                    transition: 'color 0.2s'
                }} className="hover-text-white">
                    <ArrowLeft size={20} />
                    Back to Import
                </Link>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                    <div>
                        <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>Dashboard</h1>
                        <p style={{ color: 'var(--text-secondary)' }}>Overview of Purchase Order processing activity</p>
                    </div>
                    <div style={{
                        padding: '0.5rem 1rem',
                        background: 'rgba(59, 130, 246, 0.1)',
                        borderRadius: '20px',
                        color: '#60a5fa',
                        fontSize: '0.9rem',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem'
                    }}>
                        <Activity size={16} />
                        Auto-refreshing
                    </div>
                </div>
            </div>

            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(4, 1fr)',
                gap: '1.5rem',
                marginBottom: '3rem'
            }}>
                <StatCard
                    title="Total Uploads"
                    value={metrics.totalUploads}
                    icon={FileText}
                    color="96, 165, 250" // Blue
                    delay={0}
                />
                <StatCard
                    title="Success Rate"
                    value={`${metrics.successRate}%`}
                    icon={CheckCircle}
                    color="52, 211, 153" // Green
                    delay={0.1}
                />
                <StatCard
                    title="Lines Processed"
                    value={metrics.totalLinesProcessed.toLocaleString()}
                    icon={Activity}
                    color="244, 114, 182" // Pink
                    delay={0.2}
                />
                <StatCard
                    title="Today's Activity"
                    value={metrics.todayUploads}
                    icon={Clock}
                    color="250, 204, 21" // Yellow
                    delay={0.3}
                />
            </div>

            <motion.div
                variants={containerVariants}
                initial="hidden"
                animate="visible"
                className="glass-card"
                style={{ padding: '0', overflow: 'hidden' }}
            >
                <div style={{
                    padding: '1.5rem',
                    borderBottom: '1px solid rgba(255,255,255,0.05)',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                }}>
                    <h3 style={{ margin: 0 }}>Recent Uploads</h3>
                    <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Last 20 transactions</span>
                </div>

                <div className="table-container" style={{ maxHeight: '500px', overflowY: 'auto' }}>
                    <table className="data-table" style={{ margin: 0 }}>
                        <thead style={{ position: 'sticky', top: 0, background: 'rgba(30, 30, 40, 0.95)', backdropFilter: 'blur(10px)', zIndex: 1 }}>
                            <tr>
                                <th style={{ paddingLeft: '1.5rem' }}>File Name</th>
                                <th>Status</th>
                                <th>Lines</th>
                                <th>Success</th>
                                <th>Error</th>
                                <th>Time</th>
                            </tr>
                        </thead>
                        <tbody>
                            {recentUploads.map((upload, idx) => (
                                <motion.tr
                                    key={upload.id}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: idx * 0.05 }}
                                    style={{ borderBottom: '1px solid rgba(255,255,255,0.02)' }}
                                >
                                    <td style={{ paddingLeft: '1.5rem', fontWeight: 500 }}>{upload.filename}</td>
                                    <td>
                                        <span style={{
                                            padding: '4px 12px',
                                            borderRadius: '12px',
                                            fontSize: '0.85rem',
                                            background: upload.status === 'Completed' ? 'rgba(52, 211, 153, 0.1)' :
                                                upload.status === 'Failed' ? 'rgba(239, 68, 68, 0.1)' : 'rgba(250, 204, 21, 0.1)',
                                            color: upload.status === 'Completed' ? '#34d399' :
                                                upload.status === 'Failed' ? '#ef4444' : '#facc15'
                                        }}>
                                            {upload.status}
                                        </span>
                                    </td>
                                    <td>{upload.total_lines}</td>
                                    <td style={{ color: '#34d399' }}>{upload.success_count}</td>
                                    <td style={{ color: upload.error_count > 0 ? '#ef4444' : 'var(--text-secondary)' }}>
                                        {upload.error_count}
                                    </td>
                                    <td style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                                        {new Date(upload.created_at).toLocaleString()}
                                    </td>
                                </motion.tr>
                            ))}
                            {recentUploads.length === 0 && !loading && (
                                <tr>
                                    <td colSpan="6" style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-secondary)' }}>
                                        No uploads found yet.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </motion.div>
        </div>
    )
}

export default Dashboard
