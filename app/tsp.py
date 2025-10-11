from app import flask_app
from app.utils import (
    get_error_context,
    add_row,
    add_mv_pair,
    get_row,
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


def init_tsp(tsp_variables, budget, month, les_text=None):
    TSP_TEMPLATE = flask_app.config['TSP_TEMPLATE']
    
    tsp = []
    for _, row in TSP_TEMPLATE.iterrows():
        add_row("tsp", tsp, row['header'], template=TSP_TEMPLATE)


    base_pay_total = get_row(budget, "Base Pay").get(month, 0.0)
    specialty_pay_total = sum_rows_via_modal(budget, "specialty", month)
    incentive_pay_total = sum_rows_via_modal(budget, "incentive", month)
    bonus_pay_total = sum_rows_via_modal(budget, "bonus", month)

    add_mv_pair(tsp, 'Base Pay Total', month, base_pay_total)
    add_mv_pair(tsp, 'Specialty Pay Total', month, specialty_pay_total)
    add_mv_pair(tsp, 'Incentive Pay Total', month, incentive_pay_total)
    add_mv_pair(tsp, 'Bonus Pay Total', month, bonus_pay_total)

    combat_zone = get_row(budget, "Combat Zone").get(month, "No")

    if les_text:
        tsp = add_tsp_variables(tsp, month, tsp_variables)

        trad_row = get_row(budget, "Traditional TSP")
        trad_tsp_contribution = trad_row.get(month, 0.0) if trad_row else 0.0
        roth_row = get_row(budget, "Roth TSP")
        roth_tsp_contribution = roth_row.get(month, 0.0) if roth_row else 0.0

        if combat_zone == "No":
            add_mv_pair(tsp, 'Trad TSP Contribution', month, abs(trad_tsp_contribution))
            add_mv_pair(tsp, 'Trad TSP Exempt Contribution', month, 0)
        elif combat_zone == "Yes":
            add_mv_pair(tsp, 'Trad TSP Contribution', month, 0)
            add_mv_pair(tsp, 'Trad TSP Exempt Contribution', month, abs(trad_tsp_contribution))
        add_mv_pair(tsp, 'Roth TSP Contribution', month, abs(roth_tsp_contribution))

        tsp_contribution_total = (get_row(tsp, "Trad TSP Contribution").get(month, 0.0) + 
                                  get_row(tsp, "Trad TSP Exempt Contribution").get(month, 0.0) + 
                                  get_row(tsp, "Roth TSP Contribution").get(month, 0.0) + 
                                  get_row(tsp, "Agency Auto Contribution").get(month, 0.0) + 
                                  get_row(tsp, "Agency Match Contribution").get(month, 0.0))
        add_mv_pair(tsp, 'TSP Contribution Total', month, tsp_contribution_total)

        ytd_tsp_contribution_total = round(calc_ytd_tsp_contribution_total(tsp, month), 2)
        add_mv_pair(tsp, 'YTD TSP Contribution Total', month, ytd_tsp_contribution_total)

        elective_deferral_remaining = flask_app.config['TSP_ELECTIVE_LIMIT'] - get_row(tsp, "YTD Trad TSP").get(month, 0.0) - get_row(tsp, "YTD Roth TSP").get(month, 0.0)
        add_mv_pair(tsp, 'Elective Deferral Remaining', month, elective_deferral_remaining)

        annual_deferral_remaining = flask_app.config['TSP_ANNUAL_LIMIT'] - ytd_tsp_contribution_total
        add_mv_pair(tsp, 'Annual Deferral Remaining', month, annual_deferral_remaining)
    
    else:
        tsp = add_tsp_variables(tsp, month, tsp_variables)
        tsp_contributions = calc_tsp_contributions(tsp, month, combat_zone)
        add_mv_pair(tsp, 'Trad TSP Contribution', month, tsp_contributions['trad_final'])
        add_mv_pair(tsp, 'Trad TSP Exempt Contribution', month, tsp_contributions['trad_exempt_final'])
        add_mv_pair(tsp, 'Roth TSP Contribution', month, tsp_contributions['roth_final'])
        add_mv_pair(tsp, 'Agency Auto Contribution', month, tsp_contributions['agency_auto_final'])
        add_mv_pair(tsp, 'Agency Match Contribution', month, tsp_contributions['agency_match_final'])
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
    base_pay_total = get_row(tsp, "Base Pay Total").get(month, 0.0)
    specialty_pay_total = get_row(tsp, "Specialty Pay Total").get(month, 0.0)
    incentive_pay_total = get_row(tsp, "Incentive Pay Total").get(month, 0.0)
    bonus_pay_total = get_row(tsp, "Bonus Pay Total").get(month, 0.0)

    trad_base_rate = float(get_row(tsp, "Trad TSP Base Rate").get(month, 0.0))
    trad_specialty_rate = float(get_row(tsp, "Trad TSP Specialty Rate").get(month, 0.0))
    trad_incentive_rate = float(get_row(tsp, "Trad TSP Incentive Rate").get(month, 0.0))
    trad_bonus_rate = float(get_row(tsp, "Trad TSP Bonus Rate").get(month, 0.0))
    roth_base_rate = float(get_row(tsp, "Roth TSP Base Rate").get(month, 0.0))
    roth_specialty_rate = float(get_row(tsp, "Roth TSP Specialty Rate").get(month, 0.0))
    roth_incentive_rate = float(get_row(tsp, "Roth TSP Incentive Rate").get(month, 0.0))
    roth_bonus_rate = float(get_row(tsp, "Roth TSP Bonus Rate").get(month, 0.0))

    if prev_month:
        prev_elective_remaining = get_row(tsp, "Elective Deferral Remaining").get(prev_month, flask_app.config['TSP_ELECTIVE_LIMIT'])
        prev_annual_remaining = get_row(tsp, "Annual Deferral Remaining").get(prev_month, flask_app.config['TSP_ANNUAL_LIMIT'])
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

    # TSP specialty/incentive/bonus zeroing
    #tsp_types = [
    #    ("Trad TSP Base Rate", ["Trad TSP Specialty Rate", "Trad TSP Incentive Rate", "Trad TSP Bonus Rate"]),
    #    ("Roth TSP Base Rate", ["Roth TSP Specialty Rate", "Roth TSP Incentive Rate", "Roth TSP Bonus Rate"])
    #]
    #for base_header, specialty_headers in tsp_types:
    #    base_row = next((r for r in budget if r['header'] == base_header), None)
    #    if base_row and base_row.get(working_month, 0) == 0:
    #        for header in specialty_headers:
    #            rate_row = next((r for r in budget if r['header'] == header), None)
    #            if rate_row:
    #                rate_row[working_month] = 0