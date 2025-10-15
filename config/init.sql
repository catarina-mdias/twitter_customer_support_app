-- Database initialization script for Support Analytics
-- This script creates the necessary tables and sample data

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS support_analytics;

-- Use the database
\c support_analytics;

-- Create support_tickets table
CREATE TABLE IF NOT EXISTS support_tickets (
    id SERIAL PRIMARY KEY,
    ticket_id VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP,
    customer_message TEXT,
    team VARCHAR(100),
    status VARCHAR(50) DEFAULT 'open',
    priority VARCHAR(20) DEFAULT 'medium',
    category VARCHAR(50),
    assigned_to VARCHAR(100),
    resolution_time_minutes INTEGER,
    customer_satisfaction_score INTEGER CHECK (customer_satisfaction_score >= 1 AND customer_satisfaction_score <= 5),
    tags TEXT[],
    metadata JSONB,
    created_by VARCHAR(100),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create teams table
CREATE TABLE IF NOT EXISTS teams (
    id SERIAL PRIMARY KEY,
    team_name VARCHAR(100) UNIQUE NOT NULL,
    team_lead VARCHAR(100),
    team_size INTEGER DEFAULT 1,
    specialization VARCHAR(100),
    working_hours JSONB,
    sla_target_minutes INTEGER DEFAULT 60,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create agents table
CREATE TABLE IF NOT EXISTS agents (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    team_id INTEGER REFERENCES teams(id),
    role VARCHAR(50) DEFAULT 'agent',
    is_active BOOLEAN DEFAULT true,
    hire_date DATE,
    performance_score DECIMAL(3,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create customer_feedback table
CREATE TABLE IF NOT EXISTS customer_feedback (
    id SERIAL PRIMARY KEY,
    ticket_id VARCHAR(50) REFERENCES support_tickets(ticket_id),
    feedback_text TEXT,
    sentiment_score DECIMAL(3,2),
    sentiment_category VARCHAR(20),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    feedback_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_tickets_created_at ON support_tickets(created_at);
CREATE INDEX IF NOT EXISTS idx_tickets_team ON support_tickets(team);
CREATE INDEX IF NOT EXISTS idx_tickets_status ON support_tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_priority ON support_tickets(priority);
CREATE INDEX IF NOT EXISTS idx_tickets_resolution_time ON support_tickets(resolution_time_minutes);
CREATE INDEX IF NOT EXISTS idx_agents_team ON agents(team_id);
CREATE INDEX IF NOT EXISTS idx_feedback_ticket ON customer_feedback(ticket_id);
CREATE INDEX IF NOT EXISTS idx_feedback_sentiment ON customer_feedback(sentiment_score);

-- Insert sample teams
INSERT INTO teams (team_name, team_lead, team_size, specialization, sla_target_minutes) VALUES
('Support Team A', 'John Smith', 5, 'Technical Support', 45),
('Support Team B', 'Sarah Johnson', 4, 'Billing Support', 30),
('Support Team C', 'Mike Wilson', 6, 'General Support', 60),
('Escalation Team', 'Lisa Brown', 3, 'Complex Issues', 120)
ON CONFLICT (team_name) DO NOTHING;

-- Insert sample agents
INSERT INTO agents (agent_id, name, email, team_id, role, hire_date, performance_score) VALUES
('AG001', 'Alice Cooper', 'alice.cooper@company.com', 1, 'senior_agent', '2023-01-15', 4.5),
('AG002', 'Bob Taylor', 'bob.taylor@company.com', 1, 'agent', '2023-03-20', 4.2),
('AG003', 'Carol Davis', 'carol.davis@company.com', 2, 'senior_agent', '2022-11-10', 4.7),
('AG004', 'David Miller', 'david.miller@company.com', 2, 'agent', '2023-05-05', 4.0),
('AG005', 'Eva Garcia', 'eva.garcia@company.com', 3, 'team_lead', '2022-08-15', 4.8),
('AG006', 'Frank Lee', 'frank.lee@company.com', 3, 'agent', '2023-02-28', 4.1),
('AG007', 'Grace Wong', 'grace.wong@company.com', 4, 'senior_agent', '2022-06-01', 4.9)
ON CONFLICT (agent_id) DO NOTHING;

-- Insert sample support tickets
INSERT INTO support_tickets (ticket_id, created_at, responded_at, customer_message, team, status, priority, category, assigned_to, resolution_time_minutes, customer_satisfaction_score) VALUES
('T001', '2024-01-01 10:00:00', '2024-01-01 10:15:00', 'I need help with my account login. I cannot access my dashboard.', 'Support Team A', 'resolved', 'high', 'Technical', 'Alice Cooper', 15, 5),
('T002', '2024-01-01 11:00:00', '2024-01-01 11:30:00', 'Thank you for the quick response! The issue is now resolved.', 'Support Team B', 'resolved', 'low', 'General', 'Carol Davis', 30, 5),
('T003', '2024-01-01 12:00:00', '2024-01-01 12:45:00', 'I am having issues with my payment method. The transaction keeps failing.', 'Support Team B', 'resolved', 'high', 'Billing', 'David Miller', 45, 4),
('T004', '2024-01-01 13:00:00', '2024-01-01 13:20:00', 'How do I cancel my subscription? I want to downgrade to the basic plan.', 'Support Team C', 'resolved', 'medium', 'Billing', 'Eva Garcia', 20, 4),
('T005', '2024-01-01 14:00:00', '2024-01-01 14:10:00', 'The app is crashing on my mobile device. Please help!', 'Support Team A', 'resolved', 'high', 'Technical', 'Bob Taylor', 10, 3),
('T006', '2024-01-01 15:00:00', '2024-01-01 15:25:00', 'I need to update my billing information. How can I do this?', 'Support Team B', 'resolved', 'medium', 'Billing', 'Carol Davis', 25, 5),
('T007', '2024-01-01 16:00:00', '2024-01-01 16:35:00', 'The feature I was promised is not working as expected. This is frustrating!', 'Escalation Team', 'resolved', 'high', 'Technical', 'Grace Wong', 35, 2),
('T008', '2024-01-01 17:00:00', '2024-01-01 17:15:00', 'Can you help me understand how to use the new dashboard?', 'Support Team C', 'resolved', 'low', 'General', 'Frank Lee', 15, 4),
('T009', '2024-01-01 18:00:00', '2024-01-01 18:40:00', 'I am getting error messages when trying to upload files. This is urgent!', 'Support Team A', 'resolved', 'high', 'Technical', 'Alice Cooper', 40, 3),
('T010', '2024-01-01 19:00:00', '2024-01-01 19:05:00', 'Thank you for your excellent service today!', 'Support Team C', 'resolved', 'low', 'General', 'Eva Garcia', 5, 5)
ON CONFLICT (ticket_id) DO NOTHING;

-- Insert sample customer feedback
INSERT INTO customer_feedback (ticket_id, feedback_text, sentiment_score, sentiment_category, rating) VALUES
('T001', 'Great service! The agent was very helpful and resolved my issue quickly.', 0.8, 'positive', 5),
('T002', 'Thank you for the quick response!', 0.7, 'positive', 5),
('T003', 'The payment issue was resolved, but it took longer than expected.', 0.2, 'neutral', 4),
('T004', 'The agent was knowledgeable and helped me understand the process.', 0.6, 'positive', 4),
('T005', 'The app is still having issues. Not satisfied with the resolution.', -0.3, 'negative', 3),
('T006', 'Perfect! Everything was updated correctly.', 0.9, 'positive', 5),
('T007', 'This is unacceptable! The feature still does not work properly.', -0.8, 'negative', 2),
('T008', 'The explanation was clear and helpful.', 0.5, 'positive', 4),
('T009', 'The file upload issue persists. Need better technical support.', -0.4, 'negative', 3),
('T010', 'Outstanding customer service!', 0.9, 'positive', 5)
ON CONFLICT DO NOTHING;

-- Create a view for ticket analytics
CREATE OR REPLACE VIEW ticket_analytics AS
SELECT 
    t.ticket_id,
    t.created_at,
    t.responded_at,
    t.resolution_time_minutes,
    t.team,
    t.status,
    t.priority,
    t.category,
    t.customer_satisfaction_score,
    cf.sentiment_score,
    cf.sentiment_category,
    cf.rating,
    CASE 
        WHEN t.resolution_time_minutes <= 30 THEN 'excellent'
        WHEN t.resolution_time_minutes <= 60 THEN 'good'
        WHEN t.resolution_time_minutes <= 120 THEN 'average'
        ELSE 'poor'
    END as performance_level
FROM support_tickets t
LEFT JOIN customer_feedback cf ON t.ticket_id = cf.ticket_id;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE support_analytics TO analytics_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO analytics_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO analytics_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO analytics_user;
