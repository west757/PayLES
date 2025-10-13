from app import flask_app
from app.utils import (
    get_error_context,
    add_row,
    add_mv_pair,
    get_row_value,
    sum_rows_via_modal,
)


def get_tsp_variables(les_text):
    tsp_variables = {}

    try:
        trad_tsp_base_rate = les_text.get('trad_tsp_base_rate', None)
        if trad_tsp_base_rate is None or trad_tsp_base_rate == "" or trad_tsp_base_rate < 0:
            raise ValueError(f"Invalid LES Trad TSP Base Rate: {trad_tsp_base_rate}")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining Trad TSP Base Rate from LES text"))
    tsp_variables['Trad TSP Base Rate'] = trad_tsp_base_rate

    try:
        trad_tsp_specialty_rate = les_text.get('trad_tsp_specialty_rate', None)
        if trad_tsp_specialty_rate is None or trad_tsp_specialty_rate == "" or trad_tsp_specialty_rate < 0:
            raise ValueError(f"Invalid LES Trad TSP Specialty Rate: {trad_tsp_specialty_rate}")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining Trad TSP Specialty Rate from LES text"))
    tsp_variables['Trad TSP Specialty Rate'] = trad_tsp_specialty_rate

    try:
        trad_tsp_incentive_rate = les_text.get('trad_tsp_incentive_rate', None)
        if trad_tsp_incentive_rate is None or trad_tsp_incentive_rate == "" or trad_tsp_incentive_rate < 0:
            raise ValueError(f"Invalid LES Trad TSP Incentive Rate: {trad_tsp_incentive_rate}")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining Trad TSP Incentive Rate from LES text"))
    tsp_variables['Trad TSP Incentive Rate'] = trad_tsp_incentive_rate

    try:
        trad_tsp_bonus_rate = les_text.get('trad_tsp_bonus_rate', None)
        if trad_tsp_bonus_rate is None or trad_tsp_bonus_rate == "" or trad_tsp_bonus_rate < 0:
            raise ValueError(f"Invalid LES Trad TSP Bonus Rate: {trad_tsp_bonus_rate}")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining Trad TSP Bonus Rate from LES text"))
    tsp_variables['Trad TSP Bonus Rate'] = trad_tsp_bonus_rate

    try:
        roth_tsp_base_rate = les_text.get('roth_tsp_base_rate', None)
        if roth_tsp_base_rate is None or roth_tsp_base_rate == "" or roth_tsp_base_rate < 0:
            raise ValueError(f"Invalid LES Roth TSP Base Rate: {roth_tsp_base_rate}")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining Roth TSP Base Rate from LES text"))
    tsp_variables['Roth TSP Base Rate'] = roth_tsp_base_rate

    try:
        roth_tsp_specialty_rate = les_text.get('roth_tsp_specialty_rate', None)
        if roth_tsp_specialty_rate is None or roth_tsp_specialty_rate == "" or roth_tsp_specialty_rate < 0:
            raise ValueError(f"Invalid LES Roth TSP Specialty Rate: {roth_tsp_specialty_rate}")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining Roth TSP Specialty Rate from LES text"))
    tsp_variables['Roth TSP Specialty Rate'] = roth_tsp_specialty_rate

    try:
        roth_tsp_incentive_rate = les_text.get('roth_tsp_incentive_rate', None)
        if roth_tsp_incentive_rate is None or roth_tsp_incentive_rate == "" or roth_tsp_incentive_rate < 0:
            raise ValueError(f"Invalid LES Roth TSP Incentive Rate: {roth_tsp_incentive_rate}")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining Roth TSP Incentive Rate from LES text"))
    tsp_variables['Roth TSP Incentive Rate'] = roth_tsp_incentive_rate

    try:
        roth_tsp_bonus_rate = les_text.get('roth_tsp_bonus_rate', None)
        if roth_tsp_bonus_rate is None or roth_tsp_bonus_rate == "" or roth_tsp_bonus_rate < 0:
            raise ValueError(f"Invalid LES Roth TSP Bonus Rate: {roth_tsp_bonus_rate}")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining Roth TSP Bonus Rate from LES text"))
    tsp_variables['Roth TSP Bonus Rate'] = roth_tsp_bonus_rate

    try:
        tsp_agency_auto = les_text.get('tsp_agency_auto', None)
        if tsp_agency_auto is None or tsp_agency_auto == "" or tsp_agency_auto < 0:
            raise ValueError(f"Invalid LES Agency Auto Contribution: {tsp_agency_auto}")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining Agency Auto Contribution from LES text"))
    tsp_variables['Agency Auto Contribution'] = tsp_agency_auto

    try:
        tsp_agency_match = les_text.get('tsp_agency_match', None)
        if tsp_agency_match is None or tsp_agency_match == "" or tsp_agency_match < 0:
            raise ValueError(f"Invalid LES Agency Match Contribution: {tsp_agency_match}")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining Agency Match Contribution from LES text"))
    tsp_variables['Agency Match Contribution'] = tsp_agency_match

    try:
        ytd_trad_tsp = les_text.get('trad_tsp_ytd', None)
        if ytd_trad_tsp is None or ytd_trad_tsp == "" or ytd_trad_tsp < 0:
            raise ValueError(f"Invalid LES YTD Trad TSP: {ytd_trad_tsp}")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining YTD Trad TSP from LES text"))
    tsp_variables['YTD Trad TSP'] = ytd_trad_tsp

    try:
        ytd_trad_tsp_exempt = les_text.get('trad_tsp_exempt_ytd', None)
        if ytd_trad_tsp_exempt is None or ytd_trad_tsp_exempt == "" or ytd_trad_tsp_exempt < 0:
            raise ValueError(f"Invalid LES YTD Trad TSP Exempt: {ytd_trad_tsp_exempt}")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining YTD Trad TSP Exempt from LES text"))
    tsp_variables['YTD Trad TSP Exempt'] = ytd_trad_tsp_exempt

    try:
        ytd_roth_tsp = les_text.get('roth_tsp_ytd', None)
        if ytd_roth_tsp is None or ytd_roth_tsp == "" or ytd_roth_tsp < 0:
            raise ValueError(f"Invalid LES YTD Roth TSP: {ytd_roth_tsp}")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining YTD Roth TSP from LES text"))
    tsp_variables['YTD Roth TSP'] = ytd_roth_tsp

    try:
        tsp_agency_auto_ytd = les_text.get('tsp_agency_auto_ytd', None)
        if tsp_agency_auto_ytd is None or tsp_agency_auto_ytd == "" or tsp_agency_auto_ytd < 0:
            raise ValueError(f"Invalid LES YTD Agency Auto Contribution: {tsp_agency_auto_ytd}")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining YTD Agency Auto Contribution from LES text"))
    tsp_variables['YTD Agency Auto'] = tsp_agency_auto_ytd

    try:
        tsp_agency_match_ytd = les_text.get('tsp_agency_match_ytd', None)
        if tsp_agency_match_ytd is None or tsp_agency_match_ytd == "" or tsp_agency_match_ytd < 0:
            raise ValueError(f"Invalid LES YTD Agency Match Contribution: {tsp_agency_match_ytd}")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining YTD Agency Match Contribution from LES text"))
    tsp_variables['YTD Agency Match'] = tsp_agency_match_ytd

    return tsp_variables


def init_tsp(tsp_variables, pay, month, les_text=None):
    TSP_TEMPLATE = flask_app.config['TSP_TEMPLATE']
    
    tsp = []
    for _, row in TSP_TEMPLATE.iterrows():
        add_row("tsp", tsp, row['header'], template=TSP_TEMPLATE)

    base_pay_total = get_row_value(pay, "Base Pay", month)
    specialty_pay_total = sum_rows_via_modal(pay, "specialty", month)
    incentive_pay_total = sum_rows_via_modal(pay, "incentive", month)
    bonus_pay_total = sum_rows_via_modal(pay, "bonus", month)

    add_mv_pair(tsp, 'Base Pay Total', month, base_pay_total)
    add_mv_pair(tsp, 'Specialty Pay Total', month, specialty_pay_total)
    add_mv_pair(tsp, 'Incentive Pay Total', month, incentive_pay_total)
    add_mv_pair(tsp, 'Bonus Pay Total', month, bonus_pay_total)

    combat_zone = get_row_value(pay, "Combat Zone", month)

    if les_text:
        tsp = add_tsp_variables(tsp, month, tsp_variables)

        trad_row = next((r for r in pay if r.get('header') == "Traditional TSP"), None)
        trad_tsp_contribution = trad_row.get(month, 0.0) if trad_row else 0.0

        roth_row = next((r for r in pay if r.get('header') == "Roth TSP"), None)
        roth_tsp_contribution = roth_row.get(month, 0.0) if roth_row else 0.0

        if combat_zone == "No":
            add_mv_pair(tsp, 'Trad TSP Contribution', month, abs(trad_tsp_contribution))
            add_mv_pair(tsp, 'Trad TSP Exempt Contribution', month, 0)
        elif combat_zone == "Yes":
            add_mv_pair(tsp, 'Trad TSP Contribution', month, 0)
            add_mv_pair(tsp, 'Trad TSP Exempt Contribution', month, abs(trad_tsp_contribution))
        add_mv_pair(tsp, 'Roth TSP Contribution', month, abs(roth_tsp_contribution))

        tsp_contribution_total = (get_row_value(tsp, "Trad TSP Contribution", month) + 
                                  get_row_value(tsp, "Trad TSP Exempt Contribution", month) + 
                                  get_row_value(tsp, "Roth TSP Contribution", month) + 
                                  get_row_value(tsp, "Agency Auto Contribution", month) + 
                                  get_row_value(tsp, "Agency Match Contribution", month))
        add_mv_pair(tsp, 'TSP Contribution Total', month, tsp_contribution_total)

        ytd_tsp_contribution_total = round(calc_ytd_tsp_contribution_total(tsp, month), 2)
        add_mv_pair(tsp, 'YTD TSP Contribution Total', month, ytd_tsp_contribution_total)

        elective_deferral_remaining = flask_app.config['TSP_ELECTIVE_LIMIT'] - get_row_value(tsp, "YTD Trad TSP", month) - get_row_value(tsp, "YTD Roth TSP", month)
        add_mv_pair(tsp, 'Elective Deferral Remaining', month, elective_deferral_remaining)

        annual_deferral_remaining = flask_app.config['TSP_ANNUAL_LIMIT'] - ytd_tsp_contribution_total
        add_mv_pair(tsp, 'Annual Deferral Remaining', month, annual_deferral_remaining)
    
    else:
        tsp = add_tsp_variables(tsp, month, tsp_variables)
        tsp_contributions = calc_tsp_contributions(tsp, month, combat_zone)
        add_mv_pair(tsp, 'Trad TSP Contribution', month, tsp_contributions['trad_tsp_contribution'])
        add_mv_pair(tsp, 'Trad TSP Exempt Contribution', month, tsp_contributions['trad_tsp_exempt_contribution'])
        add_mv_pair(tsp, 'Roth TSP Contribution', month, tsp_contributions['roth_tsp_contribution'])
        add_mv_pair(tsp, 'Agency Auto Contribution', month, tsp_contributions['agency_auto_contribution'])
        add_mv_pair(tsp, 'Agency Match Contribution', month, tsp_contributions['agency_match_contribution'])
        add_mv_pair(tsp, 'TSP Contribution Total', month, tsp_contributions['tsp_contribution_total'])
        add_mv_pair(tsp, 'Elective Deferral Remaining', month, tsp_contributions['elective_remaining'])
        add_mv_pair(tsp, 'Annual Deferral Remaining', month, tsp_contributions['annual_remaining'])

    return tsp


def add_tsp_variables(tsp, month, variables):
    for var, val in variables.items():
        add_mv_pair(tsp, var, month, val)
    return tsp


def calc_ytd_tsp_contribution_total(tsp, month, prev_month=None):
    total = 0.0
    for idx, row in enumerate(tsp):
        if row.get("type") == "s":
            try:
                total += abs(float(row.get(month, 0.0)))
            except (TypeError, ValueError):
                continue

    if prev_month and month != "JAN":
        prev_total = 0.0
        for idx, row in enumerate(tsp):
            if row.get("type") == "s":
                try:
                    prev_total += abs(float(row.get(prev_month, 0.0)))
                except (TypeError, ValueError):
                    continue
        total += prev_total

    return total


def calc_tsp_contributions(tsp, month, combat_zone, prev_month=None):
    base_pay_total = get_row_value(tsp, "Base Pay Total", month)
    specialty_pay_total = get_row_value(tsp, "Specialty Pay Total", month)
    incentive_pay_total = get_row_value(tsp, "Incentive Pay Total", month)
    bonus_pay_total = get_row_value(tsp, "Bonus Pay Total", month)

    trad_base_rate = float(get_row_value(tsp, "Trad TSP Base Rate", month))
    trad_specialty_rate = float(get_row_value(tsp, "Trad TSP Specialty Rate", month))
    trad_incentive_rate = float(get_row_value(tsp, "Trad TSP Incentive Rate", month))
    trad_bonus_rate = float(get_row_value(tsp, "Trad TSP Bonus Rate", month))
    roth_base_rate = float(get_row_value(tsp, "Roth TSP Base Rate", month))
    roth_specialty_rate = float(get_row_value(tsp, "Roth TSP Specialty Rate", month))
    roth_incentive_rate = float(get_row_value(tsp, "Roth TSP Incentive Rate", month))
    roth_bonus_rate = float(get_row_value(tsp, "Roth TSP Bonus Rate", month))

    if prev_month:
        prev_elective_remaining = get_row_value(tsp, "Elective Deferral Remaining", prev_month)
        prev_annual_remaining = get_row_value(tsp, "Annual Deferral Remaining", prev_month)
    else:
        prev_elective_remaining = flask_app.config['TSP_ELECTIVE_LIMIT']
        prev_annual_remaining = flask_app.config['TSP_ANNUAL_LIMIT']

    trad_total = (
        (trad_base_rate / 100.0) * base_pay_total +
        (trad_specialty_rate / 100.0) * specialty_pay_total +
        (trad_incentive_rate / 100.0) * incentive_pay_total +
        (trad_bonus_rate / 100.0) * bonus_pay_total
    )
    roth_total = (
        (roth_base_rate / 100.0) * base_pay_total +
        (roth_specialty_rate / 100.0) * specialty_pay_total +
        (roth_incentive_rate / 100.0) * incentive_pay_total +
        (roth_bonus_rate / 100.0) * bonus_pay_total
    )

    trad_tsp_contribution = trad_total if combat_zone == "No" else 0
    trad_tsp_exempt_contribution = 0 if combat_zone == "No" else trad_total
    roth_tsp_contribution = roth_total

    agency_auto_contribution = base_pay_total * flask_app.config['TSP_AGENCY_AUTO_RATE']

    TSP_AGENCY_MATCH_RATE = flask_app.config['TSP_AGENCY_MATCH_RATE']
    max_combined_rate = max(TSP_AGENCY_MATCH_RATE.keys())
    max_match_rate = TSP_AGENCY_MATCH_RATE[max_combined_rate]

    total_base_rate = trad_base_rate + roth_base_rate
    if total_base_rate >= max_combined_rate:
        match_rate = max_match_rate
    else:
        match_rate = TSP_AGENCY_MATCH_RATE.get(total_base_rate, 0.0)
    agency_match_contribution = base_pay_total * match_rate

    trad_final = min(trad_tsp_contribution, prev_elective_remaining)
    elective_remaining = prev_elective_remaining - trad_final

    roth_final = min(roth_tsp_contribution, elective_remaining)
    elective_remaining -= roth_final

    annual_remaining = prev_annual_remaining
    agency_auto_final = min(agency_auto_contribution, annual_remaining)
    annual_remaining -= agency_auto_final

    if elective_remaining <= 0:
        agency_match_final = 0.0
    else:
        agency_match_final = min(agency_match_contribution, annual_remaining)
        annual_remaining -= agency_match_final

    trad_final = min(trad_final, annual_remaining)
    annual_remaining -= trad_final

    trad_exempt_final = min(trad_tsp_exempt_contribution, annual_remaining)
    annual_remaining -= trad_exempt_final

    roth_final = min(roth_final, annual_remaining)
    annual_remaining -= roth_final

    tsp_contribution_total = trad_final + trad_exempt_final + roth_final + agency_auto_final + agency_match_final

    return {
        "trad_tsp_contribution": round(trad_final, 2),
        "trad_tsp_exempt_contribution": round(trad_exempt_final, 2),
        "roth_tsp_contribution": round(roth_final, 2),
        "agency_auto_contribution": round(agency_auto_final, 2),
        "agency_match_contribution": round(agency_match_final, 2),
        "tsp_contribution_total": round(tsp_contribution_total, 2),
        "elective_remaining": round(elective_remaining, 2),
        "annual_remaining": round(annual_remaining, 2)
    }


def update_tsp(pay, tsp, month, prev_month, cell=None):
    base_pay_total = get_row_value(pay, "Base Pay", month)
    specialty_pay_total = sum_rows_via_modal(pay, "specialty", month)
    incentive_pay_total = sum_rows_via_modal(pay, "incentive", month)
    bonus_pay_total = sum_rows_via_modal(pay, "bonus", month)

    add_mv_pair(tsp, 'Base Pay Total', month, base_pay_total)
    add_mv_pair(tsp, 'Specialty Pay Total', month, specialty_pay_total)
    add_mv_pair(tsp, 'Incentive Pay Total', month, incentive_pay_total)
    add_mv_pair(tsp, 'Bonus Pay Total', month, bonus_pay_total)

    rate_headers = [
        "Trad TSP Base Rate", "Trad TSP Specialty Rate", "Trad TSP Incentive Rate", "Trad TSP Bonus Rate",
        "Roth TSP Base Rate", "Roth TSP Specialty Rate", "Roth TSP Incentive Rate", "Roth TSP Bonus Rate"
    ]
    for header in rate_headers:
        row = next((row for row in tsp if row.get('header') == header), None)
        prev_value = row.get(prev_month, 0)
        if cell is not None and header == cell.get('header'):
            if cell.get('repeat') or cell.get('month') == month:
                row[month] = cell.get('value')
            elif month in row:
                pass
            else:
                row[month] = prev_value
        elif month in row:
            pass
        else:
            row[month] = prev_value

    # Rate zeroing
    trad_base_row = next((row for row in tsp if row.get('header') == "Trad TSP Base Rate"), None)
    roth_base_row = next((row for row in tsp if row.get('header') == "Roth TSP Base Rate"), None)
    trad_base_rate = trad_base_row.get(month, 0)
    roth_base_rate = roth_base_row.get(month, 0)
    if trad_base_rate == 0:
        for h in ["Trad TSP Specialty Rate", "Trad TSP Incentive Rate", "Trad TSP Bonus Rate"]:
            next((row for row in tsp if row.get('header') == h), None)[month] = 0
    if roth_base_rate == 0:
        for h in ["Roth TSP Specialty Rate", "Roth TSP Incentive Rate", "Roth TSP Bonus Rate"]:
            next((row for row in tsp if row.get('header') == h), None)[month] = 0

    combat_zone = get_row_value(pay, "Combat Zone", month)

    tsp_contributions = calc_tsp_contributions(tsp, month, combat_zone, prev_month=prev_month)
    add_mv_pair(tsp, 'Trad TSP Contribution', month, tsp_contributions['trad_tsp_contribution'])
    add_mv_pair(tsp, 'Trad TSP Exempt Contribution', month, tsp_contributions['trad_tsp_exempt_contribution'])
    add_mv_pair(tsp, 'Roth TSP Contribution', month, tsp_contributions['roth_tsp_contribution'])
    add_mv_pair(tsp, 'Agency Auto Contribution', month, tsp_contributions['agency_auto_contribution'])
    add_mv_pair(tsp, 'Agency Match Contribution', month, tsp_contributions['agency_match_contribution'])
    add_mv_pair(tsp, 'TSP Contribution Total', month, tsp_contributions['tsp_contribution_total'])
    add_mv_pair(tsp, 'Elective Deferral Remaining', month, tsp_contributions['elective_remaining'])
    add_mv_pair(tsp, 'Annual Deferral Remaining', month, tsp_contributions['annual_remaining'])

    ytd_trad_prev = get_row_value(tsp, "YTD Trad TSP", prev_month)
    ytd_trad_exempt_prev = get_row_value(tsp, "YTD Trad TSP Exempt", prev_month)
    ytd_roth_prev = get_row_value(tsp, "YTD Roth TSP", prev_month)
    ytd_agency_auto_prev = get_row_value(tsp, "YTD Agency Auto", prev_month)
    ytd_agency_match_prev = get_row_value(tsp, "YTD Agency Match", prev_month)
    ytd_tsp_contribution_total = get_row_value(tsp, "YTD TSP Contribution Total", prev_month)

    add_mv_pair(tsp, "YTD Trad TSP", month, tsp_contributions['trad_tsp_contribution'] if month == "JAN" else round(ytd_trad_prev + tsp_contributions['trad_tsp_contribution'], 2))
    add_mv_pair(tsp, "YTD Trad TSP Exempt", month, tsp_contributions['trad_tsp_exempt_contribution'] if month == "JAN" else round(ytd_trad_exempt_prev + tsp_contributions['trad_tsp_exempt_contribution'], 2))
    add_mv_pair(tsp, "YTD Roth TSP", month, tsp_contributions['roth_tsp_contribution'] if month == "JAN" else round(ytd_roth_prev + tsp_contributions['roth_tsp_contribution'], 2))
    add_mv_pair(tsp, "YTD Agency Auto", month, tsp_contributions['agency_auto_contribution'] if month == "JAN" else round(ytd_agency_auto_prev + tsp_contributions['agency_auto_contribution'], 2))
    add_mv_pair(tsp, "YTD Agency Match", month, tsp_contributions['agency_match_contribution'] if month == "JAN" else round(ytd_agency_match_prev + tsp_contributions['agency_match_contribution'], 2))
    add_mv_pair(tsp, "YTD TSP Contribution Total", month, tsp_contributions['tsp_contribution_total'] if month == "JAN" else round(ytd_tsp_contribution_total + tsp_contributions['tsp_contribution_total'], 2))

    return tsp