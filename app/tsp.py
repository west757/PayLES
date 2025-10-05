from app import flask_app
from app.utils import (
    add_mv_pair,
    get_table_val,
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
    values['Specialty Pay Total'] = 0
    values['Incentive Pay Total'] = 0
    values['Bonus Pay Total'] = 0

    values['Trad TSP Contribution'] = abs(get_table_val(budget, "Traditional TSP", init_month))
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

    elif initials:
        values['Agency Auto Contribution'] = 0
        values['Agency Matching Contribution'] = 0
        values.update(initials)

    for header, value in values.items():
        add_mv_pair(tsp, header, init_month, value)



    return tsp