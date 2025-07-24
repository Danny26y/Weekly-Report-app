
def map_ldap_department_to_ids(department):
    dept_map = {
        'Derivatives and Risk Management': {'Dept_ID': 1, 'Div_ID': 1},
        'Procurement & Support Services': {'Dept_ID': 2, 'Div_ID': 6},
        'Director General''s Office': {'Dept_ID': 3, 'Div_ID': 13},
        'Enforcement': {'Dept_ID': 4, 'Div_ID': 19},
        'Office of the Executive Commissioner, Corporate Services': {'Dept_ID': 5, 'Div_ID': 23},
        'Office of the Executive Commissioner, Legal & Enforcement': {'Dept_ID': 6, 'Div_ID': 26},
        'Office of the Executive Commissioner, Operations': {'Dept_ID': 7, 'Div_ID': 30},
        'External Relations': {'Dept_ID': 8, 'Div_ID': 32},
        'Finance and Accounts': {'Dept_ID': 9, 'Div_ID': 37},
        'Financial Standards and Corporate Governance': {'Dept_ID': 10, 'Div_ID': 42},
        'Investment Management Services': {'Dept_ID': 11, 'Div_ID': 47},
        'Human Resources Management': {'Dept_ID': 12, 'Div_ID': 50},
        'Information Technology': {'Dept_ID': 13, 'Div_ID': 56},
        'Internal Audit': {'Dept_ID': 14, 'Div_ID': 65},
        'Legal': {'Dept_ID': 15, 'Div_ID': 69},
        'Market Development': {'Dept_ID': 16, 'Div_ID': 71},
        'Monitoring': {'Dept_ID': 17, 'Div_ID': 78},
        'Nigerian Capital Market Institute': {'Dept_ID': 18, 'Div_ID': 84},
        'Office of The Chief Economist': {'Dept_ID': 19, 'Div_ID': 90},
        'Office of Secretary to the Commission': {'Dept_ID': 20, 'Div_ID': 96},
        'Registration, Exchanges, Market Infrastructure': {'Dept_ID': 21, 'Div_ID': 99},
        'Securities & Investment Services': {'Dept_ID': 22, 'Div_ID': 103},
        'Strategy': {'Dept_ID': 23, 'Div_ID': 108},
        'FINTECH and Innovation': {'Dept_ID': 24, 'Div_ID': 110},
        # Common aliases
        'Risk Management': {'Dept_ID': 1, 'Div_ID': 1},
        'Finance': {'Dept_ID': 9, 'Div_ID': 37},
        'IT': {'Dept_ID': 13, 'Div_ID': 56},
        'HR': {'Dept_ID': 12, 'Div_ID': 50},
        'Compliance': {'Dept_ID': 10, 'Div_ID': 42}
    }
    return dept_map.get(department, {'Dept_ID': 1, 'Div_ID': 1})  # Default to Derivatives and Risk Management, HOD,s Office
