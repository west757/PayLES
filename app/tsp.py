from app import flask_app
from app.utils import (
    add_mv_pair,
    get_table_val,
    sum_rows_from_modal,
)
from app.calculations import calculate_trad_roth_tsp


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



def update_tsp(budget, tsp, prev_month, working_month, cell_header=None, cell_month=None, cell_value=None, cell_repeat=False):
    base_pay_total = get_table_val(budget, "Base Pay", working_month)
    specialty_pay_total = sum_rows_from_modal(budget, "specialty", working_month)
    incentive_pay_total = sum_rows_from_modal(budget, "incentive", working_month)
    bonus_pay_total = sum_rows_from_modal(budget, "bonus", working_month)

    add_mv_pair(tsp, 'Base Pay Total', working_month, base_pay_total)
    add_mv_pair(tsp, 'Specialty Pay Total', working_month, specialty_pay_total)
    add_mv_pair(tsp, 'Incentive Pay Total', working_month, incentive_pay_total)
    add_mv_pair(tsp, 'Bonus Pay Total', working_month, bonus_pay_total)

    pay_totals = [base_pay_total, specialty_pay_total, incentive_pay_total, bonus_pay_total]
    rates = []

    for idx, header in enumerate(flask_app.config['TSP_RATE_HEADERS']):
        row = next((r for r in tsp if r.get('header') == header), None)

        # update rate value if changed by user, otherwise carry forward previous month
        if (cell_header is not None and header == cell_header and (working_month == cell_month or cell_repeat)):
            value = cell_value
        else:
            value = row.get(prev_month, 0.0) if row else 0.0

        add_mv_pair(tsp, header, working_month, value)
        rates.append(float(value))

    # rates slicing to get trad and roth rates
    trad_total = sum((rate / 100.0) * pay for rate, pay in zip(rates[0:4], pay_totals))
    roth_total = sum((rate / 100.0) * pay for rate, pay in zip(rates[4:8], pay_totals))

    combat_zone = get_table_val(budget, "Combat Zone", working_month)
    trad_tsp_contribution = 0 if combat_zone == "Yes" else trad_total
    trad_tsp_exempt_contribution = trad_total if combat_zone == "Yes" else 0
    roth_tsp_contribution = roth_total

    # calculates 1% agency automatic contribution
    agency_auto_contribution = base_pay_total * 0.01

    # calculates agency matching contribution based on combined rate of Trad TSP Base Rate + Roth TSP Base Rate
    combined_rate = rates[0] + rates[4]
    if combined_rate >= 5:
        agency_matching_contribution = base_pay_total * 0.04
    elif combined_rate == 4:
        agency_matching_contribution = base_pay_total * 0.035
    elif combined_rate == 3:
        agency_matching_contribution = base_pay_total * 0.03
    elif combined_rate == 2:
        agency_matching_contribution = base_pay_total * 0.02
    elif combined_rate == 1:
        agency_matching_contribution = base_pay_total * 0.01
    else:
        agency_matching_contribution = 0.0


    prev_elective_remaining = flask_app.config['TSP_ELECTIVE_LIMIT']
    prev_annual_remaining = flask_app.config['TSP_ANNUAL_LIMIT']
    if prev_month:
        prev_elective_remaining = calculate_elective_deferral_remaining(tsp, prev_month)
        prev_annual_remaining = calculate_annual_deferral_remaining(tsp, prev_month)

    trad_final = min(trad_tsp_contribution, prev_elective_remaining)
    elective_left = prev_elective_remaining - trad_final

    roth_final = min(roth_tsp_contribution, elective_left)
    elective_left -= roth_final


    annual_left = prev_annual_remaining
    agency_auto_final = min(agency_auto_contribution, annual_left)
    annual_left -= agency_auto_final

    if elective_left <= 0:
        agency_matching_final = 0.0
    else:
        agency_matching_final = min(agency_matching_contribution, annual_left)
        annual_left -= agency_matching_final

    trad_final = min(trad_final, annual_left)
    annual_left -= trad_final

    trad_exempt_final = min(trad_tsp_exempt_contribution, annual_left)
    annual_left -= trad_exempt_final

    roth_final = min(roth_final, annual_left)
    annual_left -= roth_final

    add_mv_pair(tsp, 'Trad TSP Contribution', working_month, trad_final)
    add_mv_pair(tsp, 'Trad TSP Exempt Contribution', working_month, trad_exempt_final)
    add_mv_pair(tsp, 'Roth TSP Contribution', working_month, roth_final)
    add_mv_pair(tsp, 'Agency Auto Contribution', working_month, agency_auto_final)
    add_mv_pair(tsp, 'Agency Matching Contribution', working_month, agency_matching_final)

    tsp_contribution_total = trad_final + trad_exempt_final + roth_final + agency_auto_final + agency_matching_final
    add_mv_pair(tsp, 'TSP Contribution Total', working_month, tsp_contribution_total)

    def get_prev_ytd(header):
        row = next((r for r in tsp if r.get('header') == header), None)
        if row:
            return row.get(prev_month, 0.0)
        return 0.0

    if working_month == "JAN":
        add_mv_pair(tsp, 'YTD Trad TSP', working_month, trad_final)
        add_mv_pair(tsp, 'YTD Trad TSP Exempt', working_month, trad_exempt_final)
        add_mv_pair(tsp, 'YTD Roth TSP', working_month, roth_final)
        add_mv_pair(tsp, 'YTD Agency Auto', working_month, agency_auto_final)
        add_mv_pair(tsp, 'YTD Agency Matching', working_month, agency_matching_final)
        add_mv_pair(tsp, 'YTD TSP Contribution Total', working_month, tsp_contribution_total)
    else:
        add_mv_pair(tsp, 'YTD Trad TSP', working_month, get_prev_ytd('YTD Trad TSP') + trad_final)
        add_mv_pair(tsp, 'YTD Trad TSP Exempt', working_month, get_prev_ytd('YTD Trad TSP Exempt') + trad_exempt_final)
        add_mv_pair(tsp, 'YTD Roth TSP', working_month, get_prev_ytd('YTD Roth TSP') + roth_final)
        add_mv_pair(tsp, 'YTD Agency Auto', working_month, get_prev_ytd('YTD Agency Auto') + agency_auto_final)
        add_mv_pair(tsp, 'YTD Agency Matching', working_month, get_prev_ytd('YTD Agency Matching') + agency_matching_final)
        add_mv_pair(tsp, 'YTD TSP Contribution Total', working_month, get_prev_ytd('YTD TSP Contribution Total') + tsp_contribution_total)

    add_mv_pair(tsp, 'Elective Deferral Remaining', working_month, calculate_elective_deferral_remaining(tsp, working_month))
    add_mv_pair(tsp, 'Annual Deferral Remaining', working_month, calculate_annual_deferral_remaining(tsp, working_month))

    return tsp