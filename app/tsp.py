from app import flask_app
from app.utils import (
    add_row,
    add_mv_pair,
    build_table_index,
    sum_rows_via_modal,
)


def init_tsp(budget, budget_index, month, les_text=None):
    TSP_TEMPLATE = flask_app.config['TSP_TEMPLATE']
    
    tsp = []
    for _, row in TSP_TEMPLATE.iterrows():
        add_row("tsp", tsp, row['header'], template=TSP_TEMPLATE)
    tsp_index = build_table_index(tsp)

    base_pay_total = budget[budget_index.get("Base Pay")].get(month, 0.0)
    specialty_pay_total = sum_rows_via_modal(budget, "specialty", month)
    incentive_pay_total = sum_rows_via_modal(budget, "incentive", month)
    bonus_pay_total = sum_rows_via_modal(budget, "bonus", month)

    add_mv_pair(tsp, 'Base Pay Total', month, base_pay_total)
    add_mv_pair(tsp, 'Specialty Pay Total', month, specialty_pay_total)
    add_mv_pair(tsp, 'Incentive Pay Total', month, incentive_pay_total)
    add_mv_pair(tsp, 'Bonus Pay Total', month, bonus_pay_total)

    combat_zone = budget[budget_index.get("Combat Zone")].get(month, "No")

    if les_text:
        tsp = add_tsp_from_les(tsp, month, les_text)
    else:
        print("test")

    tsp_contributions = calc_tsp_contributions(tsp, tsp_index, month, base_pay_total, specialty_pay_total, incentive_pay_total, bonus_pay_total, combat_zone, prev_elective_remaining, prev_annual_remaining)

    add_mv_pair(tsp, 'Trad TSP Contribution', month, tsp_contributions['trad_final'])
    add_mv_pair(tsp, 'Trad TSP Exempt Contribution', month, tsp_contributions['trad_exempt_final'])
    add_mv_pair(tsp, 'Roth TSP Contribution', month, tsp_contributions['roth_final'])
    add_mv_pair(tsp, 'Agency Auto Contribution', month, tsp_contributions['agency_auto_final'])
    add_mv_pair(tsp, 'Agency Matching Contribution', month, tsp_contributions['agency_matching_final'])
    add_mv_pair(tsp, 'TSP Contribution Total', month, tsp_contributions['tsp_contribution_total'])

    add_mv_pair(tsp, 'YTD TSP Contribution Total', month, calc_ytd_tsp_contribution_total(tsp, month))
    add_mv_pair(tsp, 'Elective Deferral Remaining', month, calc_elective_deferral_remaining(tsp, month))
    add_mv_pair(tsp, 'Annual Deferral Remaining', month, calc_annual_deferral_remaining(tsp, month))

    return tsp, tsp_index



def add_tsp_from_les(tsp, month, les_text):
    TSP_RATE_HEADERS = flask_app.config['TSP_RATE_HEADERS']

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
        
    try:
        agency_auto_contribution = float(les_text[85][1])
        if not agency_auto_contribution:
            raise ValueError()
    except Exception:
        agency_auto_contribution = 0.0
    add_mv_pair(tsp, 'Agency Auto Contribution', month, agency_auto_contribution)

    try:
        agency_matching_contribution = float(les_text[86][1])
        if not agency_matching_contribution:
            raise ValueError()
    except Exception:
        agency_matching_contribution = 0.0
    add_mv_pair(tsp, 'Agency Matching Contribution', month, agency_matching_contribution)

    try:
        ytd_trad_tsp = float(les_text[79][3])
        if not ytd_trad_tsp:
            raise ValueError()
    except Exception:
        ytd_trad_tsp = 0.0
    add_mv_pair(tsp, 'YTD Trad TSP', month, ytd_trad_tsp)

    try:
        ytd_trad_tsp_exempt = float(les_text[80][3])
        if not ytd_trad_tsp_exempt:
            raise ValueError()
    except Exception:
        ytd_trad_tsp_exempt = 0.0
    add_mv_pair(tsp, 'YTD Trad TSP Exempt', month, ytd_trad_tsp_exempt)

    try:
        ytd_roth_tsp = float(les_text[81][2])
        if not ytd_roth_tsp:
            raise ValueError()
    except Exception:
        ytd_roth_tsp = 0.0
    add_mv_pair(tsp, 'YTD Roth TSP', month, ytd_roth_tsp)

    try:
        ytd_agency_auto = float(les_text[82][3])
        if not ytd_agency_auto:
            raise ValueError()
    except Exception:
        ytd_agency_auto = 0.0
    add_mv_pair(tsp, 'YTD Agency Auto', month, ytd_agency_auto)

    try:
        ytd_agency_matching = float(les_text[83][3])
        if not ytd_agency_matching:
            raise ValueError()
    except Exception:
        ytd_agency_matching = 0.0
    add_mv_pair(tsp, 'YTD Agency Matching', month, ytd_agency_matching)

    return tsp







def calc_ytd_tsp_contribution_total(tsp, month, prev_month=None):
    ytd_headers = flask_app.config['TSP_YTD_HEADERS']
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


def calc_elective_deferral_remaining(tsp, month):
    total = 0.0
    for header in flask_app.config['TSP_YTD_ELECTIVE_HEADERS']:
        row = next((r for r in tsp if r.get('header') == header), None)
        if row:
            try:
                total += abs(float(row.get(month, 0.0)))
            except (TypeError, ValueError):
                continue
    return flask_app.config['TSP_ELECTIVE_LIMIT'] - total


def calc_annual_deferral_remaining(tsp, month):
    total = 0.0
    for header in flask_app.config['TSP_YTD_HEADERS']:
        row = next((r for r in tsp if r.get('header') == header), None)
        if row:
            try:
                total += abs(float(row.get(month, 0.0)))
            except (TypeError, ValueError):
                continue
    return flask_app.config['TSP_ANNUAL_LIMIT'] - total




def calc_tsp_contributions(tsp, tsp_index, month, base_pay_total, specialty_pay_total, incentive_pay_total, bonus_pay_total, combat_zone, prev_elective_remaining, prev_annual_remaining):
    rates_dict = get_tsp_rates(tsp, tsp_index, month)
    rate_headers = flask_app.config['TSP_RATE_HEADERS']
    rates = [rates_dict.get(header, 0.0) for header in rate_headers]

    pay_totals = [base_pay_total, specialty_pay_total, incentive_pay_total, bonus_pay_total]
    trad_total = sum((rate / 100.0) * pay for rate, pay in zip(rates[0:4], pay_totals))
    roth_total = sum((rate / 100.0) * pay for rate, pay in zip(rates[4:8], pay_totals))

    trad_tsp_contribution = 0 if combat_zone == "Yes" else trad_total
    trad_tsp_exempt_contribution = trad_total if combat_zone == "Yes" else 0
    roth_tsp_contribution = roth_total

    agency_auto_contribution = base_pay_total * 0.01

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

    tsp_contribution_total = trad_final + trad_exempt_final + roth_final + agency_auto_final + agency_matching_final

    return {
        "trad_final": trad_final,
        "trad_exempt_final": trad_exempt_final,
        "roth_final": roth_final,
        "agency_auto_final": agency_auto_final,
        "agency_matching_final": agency_matching_final,
        "tsp_contribution_total": tsp_contribution_total,
        "elective_left": elective_left,
        "annual_left": annual_left
    }







def update_tsp(budget, budget_index, tsp, prev_month, month, cell_header=None, cell_month=None, cell_value=None, cell_repeat=False):
    base_pay_total = budget[budget_index.get("Base Pay")].get(month, 0.0)
    specialty_pay_total = sum_rows_via_modal(budget, "specialty", month)
    incentive_pay_total = sum_rows_via_modal(budget, "incentive", month)
    bonus_pay_total = sum_rows_via_modal(budget, "bonus", month)

    add_mv_pair(tsp, 'Base Pay Total', month, base_pay_total)
    add_mv_pair(tsp, 'Specialty Pay Total', month, specialty_pay_total)
    add_mv_pair(tsp, 'Incentive Pay Total', month, incentive_pay_total)
    add_mv_pair(tsp, 'Bonus Pay Total', month, bonus_pay_total)

    pay_totals = [base_pay_total, specialty_pay_total, incentive_pay_total, bonus_pay_total]
    rates = []

    for idx, header in enumerate(flask_app.config['TSP_RATE_HEADERS']):
        row = next((r for r in tsp if r.get('header') == header), None)

        # update rate value if changed by user, otherwise carry forward previous month
        if (cell_header is not None and header == cell_header and (month == cell_month or cell_repeat)):
            value = cell_value
        else:
            value = row.get(prev_month, 0.0) if row else 0.0

        add_mv_pair(tsp, header, month, value)
        rates.append(float(value))

    # rates slicing to get trad and roth rates
    trad_total = sum((rate / 100.0) * pay for rate, pay in zip(rates[0:4], pay_totals))
    roth_total = sum((rate / 100.0) * pay for rate, pay in zip(rates[4:8], pay_totals))

    combat_zone = budget[budget_index.get("Combat Zone")].get(month, "No")
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
        prev_elective_remaining = calc_elective_deferral_remaining(tsp, prev_month)
        prev_annual_remaining = calc_annual_deferral_remaining(tsp, prev_month)

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

    add_mv_pair(tsp, 'Trad TSP Contribution', month, trad_final)
    add_mv_pair(tsp, 'Trad TSP Exempt Contribution', month, trad_exempt_final)
    add_mv_pair(tsp, 'Roth TSP Contribution', month, roth_final)
    add_mv_pair(tsp, 'Agency Auto Contribution', month, agency_auto_final)
    add_mv_pair(tsp, 'Agency Matching Contribution', month, agency_matching_final)

    tsp_contribution_total = trad_final + trad_exempt_final + roth_final + agency_auto_final + agency_matching_final
    add_mv_pair(tsp, 'TSP Contribution Total', month, tsp_contribution_total)

    def get_prev_ytd(header):
        row = next((r for r in tsp if r.get('header') == header), None)
        if row:
            return row.get(prev_month, 0.0)
        return 0.0

    if month == "JAN":
        add_mv_pair(tsp, 'YTD Trad TSP', month, trad_final)
        add_mv_pair(tsp, 'YTD Trad TSP Exempt', month, trad_exempt_final)
        add_mv_pair(tsp, 'YTD Roth TSP', month, roth_final)
        add_mv_pair(tsp, 'YTD Agency Auto', month, agency_auto_final)
        add_mv_pair(tsp, 'YTD Agency Matching', month, agency_matching_final)
        add_mv_pair(tsp, 'YTD TSP Contribution Total', month, tsp_contribution_total)
    else:
        add_mv_pair(tsp, 'YTD Trad TSP', month, get_prev_ytd('YTD Trad TSP') + trad_final)
        add_mv_pair(tsp, 'YTD Trad TSP Exempt', month, get_prev_ytd('YTD Trad TSP Exempt') + trad_exempt_final)
        add_mv_pair(tsp, 'YTD Roth TSP', month, get_prev_ytd('YTD Roth TSP') + roth_final)
        add_mv_pair(tsp, 'YTD Agency Auto', month, get_prev_ytd('YTD Agency Auto') + agency_auto_final)
        add_mv_pair(tsp, 'YTD Agency Matching', month, get_prev_ytd('YTD Agency Matching') + agency_matching_final)
        add_mv_pair(tsp, 'YTD TSP Contribution Total', month, get_prev_ytd('YTD TSP Contribution Total') + tsp_contribution_total)

    add_mv_pair(tsp, 'Elective Deferral Remaining', month, calc_elective_deferral_remaining(tsp, month))
    add_mv_pair(tsp, 'Annual Deferral Remaining', month, calc_annual_deferral_remaining(tsp, month))

    return tsp



def get_tsp_rates(tsp, tsp_index, month):
    rate_headers = flask_app.config['TSP_RATE_HEADERS']
    rates = {}
    for header in rate_headers:
        row_idx = tsp_index.get(header)
        if row_idx is not None:
            row = tsp[row_idx]
            rates[header] = float(row.get(month, 0.0))
        else:
            rates[header] = 0.0
    return rates