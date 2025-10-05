from app import flask_app
from app.utils import (
    add_mv_pair,
    get_table_val,
    sum_rows_from_modal,
)

def init_tsp(init_month, budget, les_text=None, initials=None):
    TSP_TEMPLATE = flask_app.config['TSP_TEMPLATE']
    TSP_METADATA = flask_app.config['TSP_METADATA']

    tsp = []
    for _, row in TSP_TEMPLATE.iterrows():
        tsp_row = {meta: row[meta] for meta in TSP_METADATA}
        tsp.append(tsp_row)


    values = {}

    values['Base Pay Total'] = get_table_val(budget, "Base Pay", init_month)
    values['Specialty Pay Total'] = sum_rows_from_modal(budget, "specialty", init_month)
    values['Incentive Pay Total'] = sum_rows_from_modal(budget, "incentive", init_month)
    values['Bonus Pay Total'] = sum_rows_from_modal(budget, "bonus", init_month)

    combat_zone = get_table_val(budget, "Combat Zone", init_month)
    if combat_zone == "Yes":
        values['Trad TSP Contribution'] = 0
        values['Trad TSP Exempt Contribution'] = abs(get_table_val(budget, "Traditional TSP", init_month))
    else:
        values['Trad TSP Contribution'] = abs(get_table_val(budget, "Traditional TSP", init_month))
        values['Trad TSP Exempt Contribution'] = 0
    values['Roth TSP Contribution'] = abs(get_table_val(budget, "Roth TSP", init_month))

    if les_text:
        tsp_rate_rows = [
            ("Trad TSP Base Rate", 60),
            ("Trad TSP Specialty Rate", 62),
            ("Trad TSP Incentive Rate", 64),
            ("Trad TSP Bonus Rate", 66),
            ("Roth TSP Base Rate", 69),
            ("Roth TSP Specialty Rate", 71),
            ("Roth TSP Incentive Rate", 73),
            ("Roth TSP Bonus Rate", 75),
        ]
        for header, idx in tsp_rate_rows:
            try:
                rate = float(les_text[idx][3])
                if not rate:
                    raise ValueError()
            except Exception:
                rate = 0.0
            values[header] = rate

        try:
            agency_auto_contribution = float(les_text[85][1])
            if not agency_auto_contribution:
                raise ValueError()
        except Exception:
            agency_auto_contribution = 0.0
        values['Agency Auto Contribution'] = agency_auto_contribution

        try:
            agency_matching_contribution = float(les_text[86][1])
            if not agency_matching_contribution:
                raise ValueError()
        except Exception:
            agency_matching_contribution = 0.0
        values['Agency Matching Contribution'] = agency_matching_contribution

        try:
            ytd_trad_tsp = float(les_text[79][3])
            if not ytd_trad_tsp:
                raise ValueError()
        except Exception:
            ytd_trad_tsp = 0.0
        values['YTD Trad TSP'] = ytd_trad_tsp

        try:
            ytd_trad_tsp_exempt = float(les_text[80][3])
            if not ytd_trad_tsp_exempt:
                raise ValueError()
        except Exception:
            ytd_trad_tsp_exempt = 0.0
        values['YTD Trad TSP Exempt'] = ytd_trad_tsp_exempt

        try:
            ytd_roth_tsp = float(les_text[81][2])
            if not ytd_roth_tsp:
                raise ValueError()
        except Exception:
            ytd_roth_tsp = 0.0
        values['YTD Roth TSP'] = ytd_roth_tsp

        try:
            ytd_agency_auto = float(les_text[82][3])
            if not ytd_agency_auto:
                raise ValueError()
        except Exception:
            ytd_agency_auto = 0.0
        values['YTD Agency Auto'] = ytd_agency_auto

        try:
            ytd_agency_matching = float(les_text[83][3])
            if not ytd_agency_matching:
                raise ValueError()
        except Exception:
            ytd_agency_matching = 0.0
        values['YTD Agency Matching'] = ytd_agency_matching

    elif initials:
        values['Agency Auto Contribution'] = 0
        values['Agency Matching Contribution'] = 0
        values['YTD Trad TSP'] = 0
        values['YTD Trad TSP Exempt'] = 0
        values['YTD Roth TSP'] = 0
        values['YTD Agency Auto'] = 0
        values['YTD Agency Matching'] = 0
        values.update(initials)

    for header, value in values.items():
        add_mv_pair(tsp, header, init_month, value)

    print("tsp contribution total: ", calculate_tsp_contribution_total(tsp, init_month))
    print("ytd tsp contribution total: ", calculate_ytd_tsp_contribution_total(tsp, init_month))
    print("elective deferral remaining: ", calculate_elective_deferral_remaining(tsp, init_month))
    print("annual deferral remaining: ", calculate_annual_deferral_remaining(tsp, init_month))

    add_mv_pair(tsp, 'TSP Contribution Total', init_month, calculate_tsp_contribution_total(tsp, init_month))
    add_mv_pair(tsp, 'YTD TSP Contribution Total', init_month, calculate_ytd_tsp_contribution_total(tsp, init_month))
    add_mv_pair(tsp, 'Elective Deferral Remaining', init_month, calculate_elective_deferral_remaining(tsp, init_month))
    add_mv_pair(tsp, 'Annual Deferral Remaining', init_month, calculate_annual_deferral_remaining(tsp, init_month))

    return tsp


def calculate_tsp_contribution_total(tsp, month):
    total = 0.0
    for header in flask_app.config['TSP_CONTRIBUTION_HEADERS']:
        row = next((r for r in tsp if r.get('header') == header), None)
        if row:
            try:
                total += abs(float(row.get(month, 0.0)))
            except (TypeError, ValueError):
                continue
    return total


def calculate_ytd_tsp_contribution_total(tsp, month, prev_month=None):
    ytd_headers = flask_app.config['YTD_TSP_HEADERS']
    total = 0.0
    for header in ytd_headers:
        row = next((r for r in tsp if r.get('header') == header), None)
        if row:
            try:
                total += abs(float(row.get(month, 0.0)))
            except (TypeError, ValueError):
                continue

    if prev_month and month != "JAN":
        prev_total = 0.0
        for header in ytd_headers:
            row = next((r for r in tsp if r.get('header') == header), None)
            if row:
                try:
                    prev_total += abs(float(row.get(prev_month, 0.0)))
                except (TypeError, ValueError):
                    continue
        total += prev_total

    return total


def calculate_elective_deferral_remaining(tsp, month):
    total = 0.0
    for header in flask_app.config['YTD_ELECTIVE_HEADERS']:
        row = next((r for r in tsp if r.get('header') == header), None)
        if row:
            try:
                total += abs(float(row.get(month, 0.0)))
            except (TypeError, ValueError):
                continue
    return flask_app.config['TSP_ELECTIVE_LIMIT'] - total


def calculate_annual_deferral_remaining(tsp, month):
    total = 0.0
    for header in flask_app.config['YTD_TSP_HEADERS']:
        row = next((r for r in tsp if r.get('header') == header), None)
        if row:
            try:
                total += abs(float(row.get(month, 0.0)))
            except (TypeError, ValueError):
                continue
    return flask_app.config['TSP_ANNUAL_LIMIT'] - total