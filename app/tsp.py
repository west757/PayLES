from app import flask_app
from app.utils import (
    get_error_context,
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

    for row in tsp_index:
        print(row)

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
        tsp_variables = get_les_tsp_variables(les_text)
        tsp = add_tsp_variables(tsp, month, tsp_variables)

        trad_tsp_contribution = budget[budget_index.get("Traditional TSP")].get(month, 0.0)
        roth_tsp_contribution = budget[budget_index.get("Roth TSP")].get(month, 0.0)
        if combat_zone == "No":
            add_mv_pair(tsp, 'Trad TSP Contribution', month, trad_tsp_contribution)
            add_mv_pair(tsp, 'Trad TSP Exempt Contribution', month, 0)
        elif combat_zone == "Yes":
            add_mv_pair(tsp, 'Trad TSP Contribution', month, 0)
            add_mv_pair(tsp, 'Trad TSP Exempt Contribution', month, trad_tsp_contribution)
        add_mv_pair(tsp, 'Roth TSP Exempt Contribution', month, roth_tsp_contribution)

        ytd_tsp_contribution_total = calc_ytd_tsp_contribution_total(tsp, month)
        add_mv_pair(tsp, 'YTD TSP Contribution Total', month, ytd_tsp_contribution_total)

        elective_deferral_remaining = flask_app.config['TSP_ELECTIVE_LIMIT'] - tsp[tsp_index.get("YTD Trad TSP")].get(month, 0.0) - tsp[tsp_index.get("YTD Roth TSP")].get(month, 0.0)
        add_mv_pair(tsp, 'Elective Deferral Remaining', month, elective_deferral_remaining)

        annual_deferral_remaining = flask_app.config['TSP_ANNUAL_LIMIT'] - ytd_tsp_contribution_total
        add_mv_pair(tsp, 'Annual Deferral Remaining', month, annual_deferral_remaining)
    
    else:
        tsp = add_tsp_variables(tsp, month, tsp_variables)
        tsp_contributions = calc_tsp_contributions(tsp, tsp_index, month, combat_zone)
        add_mv_pair(tsp, 'Trad TSP Contribution', month, tsp_contributions['trad_final'])
        add_mv_pair(tsp, 'Trad TSP Exempt Contribution', month, tsp_contributions['trad_exempt_final'])
        add_mv_pair(tsp, 'Roth TSP Contribution', month, tsp_contributions['roth_final'])
        add_mv_pair(tsp, 'Agency Auto Contribution', month, tsp_contributions['agency_auto_final'])
        add_mv_pair(tsp, 'Agency match Contribution', month, tsp_contributions['agency_match_final'])
        add_mv_pair(tsp, 'TSP Contribution Total', month, tsp_contributions['tsp_contribution_total'])
        add_mv_pair(tsp, 'Elective Deferral Remaining', month, tsp_contributions['elective_remaining'])
        add_mv_pair(tsp, 'Annual Deferral Remaining', month, tsp_contributions['annual_remaining'])

    
    add_mv_pair(tsp, 'Elective Deferral Remaining', month, calc_elective_deferral_remaining(tsp, month))
    add_mv_pair(tsp, 'Annual Deferral Remaining', month, calc_annual_deferral_remaining(tsp, month))

    return tsp, tsp_index


def get_les_tsp_variables(les_text):
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
        tsp_agency_auto = les_text.get('agency_auto_contribution', None)
        if tsp_agency_auto is None or tsp_agency_auto == "" or tsp_agency_auto < 0:
            raise ValueError(f"Invalid LES Agency Auto Contribution: {tsp_agency_auto}")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining Agency Auto Contribution from LES text"))
    tsp_variables['Agency Auto Contribution'] = tsp_agency_auto

    try:
        tsp_agency_match = les_text.get('agency_match_contribution', None)
        if tsp_agency_match is None or tsp_agency_match == "" or tsp_agency_match < 0:
            raise ValueError(f"Invalid LES Agency match Contribution: {tsp_agency_match}")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining Agency match Contribution from LES text"))
    tsp_variables['Agency match Contribution'] = tsp_agency_match

    try:
        ytd_trad_tsp = les_text.get('trad_tsp_ytd', None)
        if ytd_trad_tsp is None or ytd_trad_tsp == "" or ytd_trad_tsp < 0:
            raise ValueError(f"Invalid LES YTD Trad TSP: {ytd_trad_tsp}")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining YTD Trad TSP from LES text"))
    tsp_variables['YTD Trad TSP'] = ytd_trad_tsp

    try:
        ytd_trad_tsp_exempt = les_text.get('trad_tsp_ytd_exempt', None)
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
            raise ValueError(f"Invalid LES YTD Agency match Contribution: {tsp_agency_match_ytd}")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining YTD Agency match Contribution from LES text"))
    tsp_variables['YTD Agency match'] = tsp_agency_match_ytd

    return tsp_variables


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


def calc_tsp_contributions(tsp, tsp_index, month, combat_zone, prev_month=None):
    base_pay_total = tsp[tsp_index.get("Base Pay Total")].get(month, 0.0)
    specialty_pay_total = tsp[tsp_index.get("Specialty Pay Total")].get(month, 0.0)
    incentive_pay_total = tsp[tsp_index.get("Incentive Pay Total")].get(month, 0.0)
    bonus_pay_total = tsp[tsp_index.get("Bonus Pay Total")].get(month, 0.0)

    trad_base_rate = float(tsp[tsp_index.get("Trad TSP Base Rate")].get(month, 0.0))
    trad_specialty_rate = float(tsp[tsp_index.get("Trad TSP Specialty Rate")].get(month, 0.0))
    trad_incentive_rate = float(tsp[tsp_index.get("Trad TSP Incentive Rate")].get(month, 0.0))
    trad_bonus_rate = float(tsp[tsp_index.get("Trad TSP Bonus Rate")].get(month, 0.0))
    roth_base_rate = float(tsp[tsp_index.get("Roth TSP Base Rate")].get(month, 0.0))
    roth_specialty_rate = float(tsp[tsp_index.get("Roth TSP Specialty Rate")].get(month, 0.0))
    roth_incentive_rate = float(tsp[tsp_index.get("Roth TSP Incentive Rate")].get(month, 0.0))
    roth_bonus_rate = float(tsp[tsp_index.get("Roth TSP Bonus Rate")].get(month, 0.0))

    # Calculate previous elective and annual remaining
    if prev_month:
        prev_elective_remaining = tsp[tsp_index.get("Elective Deferral Remaining")].get(prev_month, flask_app.config['TSP_ELECTIVE_LIMIT'])
        prev_annual_remaining = tsp[tsp_index.get("Annual Deferral Remaining")].get(prev_month, flask_app.config['TSP_ANNUAL_LIMIT'])
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

    agency_auto_contribution = base_pay_total * flask_app.config['TSP_AGENCY_AUTO_RATE'] / 100.0

    match_rate = flask_app.config['TSP_AGENCY_MATCH_RATE'].get(int(trad_base_rate + roth_base_rate), 0.0) / 100.0
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
        "trad_final": trad_final,
        "trad_exempt_final": trad_exempt_final,
        "roth_final": roth_final,
        "agency_auto_final": agency_auto_final,
        "agency_match_final": agency_match_final,
        "tsp_contribution_total": tsp_contribution_total,
        "elective_remaining": elective_remaining,
        "annual_remaining": annual_remaining
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

    # calculates agency match contribution based on combined rate of Trad TSP Base Rate + Roth TSP Base Rate
    combined_rate = rates[0] + rates[4]
    if combined_rate >= 5:
        agency_match_contribution = base_pay_total * 0.04
    elif combined_rate == 4:
        agency_match_contribution = base_pay_total * 0.035
    elif combined_rate == 3:
        agency_match_contribution = base_pay_total * 0.03
    elif combined_rate == 2:
        agency_match_contribution = base_pay_total * 0.02
    elif combined_rate == 1:
        agency_match_contribution = base_pay_total * 0.01
    else:
        agency_match_contribution = 0.0


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
        agency_match_final = 0.0
    else:
        agency_match_final = min(agency_match_contribution, annual_left)
        annual_left -= agency_match_final

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
    add_mv_pair(tsp, 'Agency match Contribution', month, agency_match_final)

    tsp_contribution_total = trad_final + trad_exempt_final + roth_final + agency_auto_final + agency_match_final
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
        add_mv_pair(tsp, 'YTD Agency match', month, agency_match_final)
        add_mv_pair(tsp, 'YTD TSP Contribution Total', month, tsp_contribution_total)
    else:
        add_mv_pair(tsp, 'YTD Trad TSP', month, get_prev_ytd('YTD Trad TSP') + trad_final)
        add_mv_pair(tsp, 'YTD Trad TSP Exempt', month, get_prev_ytd('YTD Trad TSP Exempt') + trad_exempt_final)
        add_mv_pair(tsp, 'YTD Roth TSP', month, get_prev_ytd('YTD Roth TSP') + roth_final)
        add_mv_pair(tsp, 'YTD Agency Auto', month, get_prev_ytd('YTD Agency Auto') + agency_auto_final)
        add_mv_pair(tsp, 'YTD Agency match', month, get_prev_ytd('YTD Agency match') + agency_match_final)
        add_mv_pair(tsp, 'YTD TSP Contribution Total', month, get_prev_ytd('YTD TSP Contribution Total') + tsp_contribution_total)

    add_mv_pair(tsp, 'Elective Deferral Remaining', month, calc_elective_deferral_remaining(tsp, month))
    add_mv_pair(tsp, 'Annual Deferral Remaining', month, calc_annual_deferral_remaining(tsp, month))

    return tsp
