/**
 * ALIAS Type Definitions
 * JSDoc type definitions for login events and investigations.
 */

/**
 * @typedef {Object} LoginEvent
 * @property {number} id
 * @property {string} user_id
 * @property {string} ip_address
 * @property {number|null} latitude
 * @property {number|null} longitude
 * @property {string|null} location
 * @property {string|null} device_fingerprint
 * @property {string|null} user_agent
 * @property {string} timestamp
 * @property {string} auth_status
 * @property {number} failed_attempts
 * @property {string|null} access_pattern
 * @property {string} processing_status
 * @property {string} created_at
 */

/**
 * @typedef {Object} AnomalyRecord
 * @property {number} id
 * @property {number} event_id
 * @property {string} anomaly_type
 * @property {string} severity
 * @property {number} score
 * @property {Object} evidence
 * @property {string|null} description
 */

/**
 * @typedef {Object} InvestigationReport
 * @property {number} id
 * @property {number} event_id
 * @property {number} risk_score
 * @property {string} severity
 * @property {string|null} summary
 * @property {string[]} indicators
 * @property {string|null} attack_scenario
 * @property {string[]} recommendations
 */

export {};
