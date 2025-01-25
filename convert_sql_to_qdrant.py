import json
import re
from qdrant_client import QdrantClient, models
from qdrant_client.models import Distance, VectorParams, PointStruct


def convert_init_query_to_proper_sql_where_clause(init_query, key):
    def convert_part_to_where_cond(string, start_ind, lb_till_symb):
        next_ind = -1
        next_sym = "("
        add_sym_len = len(f" {key} ILIKE '%%'")

        and_ind = string.find(" AND ", start_ind)
        or_ind = string.find(" OR ", start_ind)
        br_c_ind = string.find(")", start_ind)

        if and_ind > 0 or or_ind > 0 or br_c_ind > 0:
            if (
                and_ind == min(n for n in [and_ind, or_ind, br_c_ind] if n > 0)
                and and_ind > 0
            ):
                lbnd_br_o_ind = string.rfind("(", start_ind, and_ind)
                lbnd_br_c_ind = string.rfind(")", start_ind, and_ind)
                if lb_till_symb == "(":
                    lbnd_sym_ind = lbnd_br_o_ind
                elif lb_till_symb == ")":
                    lbnd_sym_ind = lbnd_br_c_ind
                elif lb_till_symb == "AND":
                    lbnd_sym_ind = string.rfind("AND", start_ind, and_ind) + 3
                elif lb_till_symb == "OR":
                    lbnd_sym_ind = string.rfind("OR", start_ind, and_ind) + 2
                lbnd_ind = max(lbnd_br_o_ind, lbnd_sym_ind)

                if string[start_ind:and_ind].replace(" ", "") != "":
                    next_ind = and_ind + 1 + add_sym_len
                    substr_for_edit = string[lbnd_ind:and_ind]

                    if (
                        "NOT " in substr_for_edit[1:]
                        and not "\\NOT " in substr_for_edit[1:]
                    ) or substr_for_edit[1:].startswith("-"):
                        if substr_for_edit[1:].startswith("-"):
                            substr_for_edit = substr_for_edit[0] + substr_for_edit[
                                2:
                            ].replace(
                                substr_for_edit[2:],
                                f" {key} NOT ILIKE '%{substr_for_edit[2:]}%'",
                            )
                            next_ind = next_ind - 1 + len("NOT ")
                        else:
                            substr_for_edit = substr_for_edit.replace("NOT ", "")
                            substr_for_edit = substr_for_edit.replace(
                                substr_for_edit[1:],
                                f" {key} NOT ILIKE '%{substr_for_edit[1:]}%'",
                            )
                    else:
                        substr_for_edit = substr_for_edit.replace(
                            substr_for_edit[1:], f" {key} ILIKE '%{substr_for_edit[1:]}%'"
                        )
                    string = (
                        string[:start_ind]
                        + string[start_ind:lbnd_ind]
                        + substr_for_edit
                        + string[and_ind:]
                    )
                else:
                    next_ind = and_ind + 1
                next_sym = "AND"
            elif (
                or_ind == min(n for n in [and_ind, or_ind, br_c_ind] if n > 0)
                and or_ind > 0
            ):
                lbnd_br_o_ind = string.rfind("(", start_ind, or_ind)
                lbnd_br_c_ind = string.rfind(")", start_ind, or_ind)
                if lb_till_symb == "(":
                    lbnd_sym_ind = lbnd_br_o_ind
                elif lb_till_symb == ")":
                    lbnd_sym_ind = lbnd_br_c_ind
                elif lb_till_symb == "AND":
                    lbnd_sym_ind = string.rfind("AND", start_ind, or_ind) + 3
                elif lb_till_symb == "OR":
                    lbnd_sym_ind = string.rfind("OR", start_ind, or_ind) + 2
                lbnd_ind = max(lbnd_br_o_ind, lbnd_sym_ind)

                if string[start_ind:or_ind].replace(" ", "") != "":
                    next_ind = or_ind + 1 + add_sym_len
                    substr_for_edit = string[lbnd_ind:or_ind]

                    if (
                        "NOT " in substr_for_edit[1:]
                        and not "\\NOT " in substr_for_edit[1:]
                    ) or substr_for_edit[1:].startswith("-"):
                        if substr_for_edit[1:].startswith("-"):
                            substr_for_edit = substr_for_edit[0] + substr_for_edit[
                                2:
                            ].replace(
                                substr_for_edit[2:],
                                f" {key} NOT ILIKE '%{substr_for_edit[2:]}%'",
                            )
                            next_ind = next_ind - 1 + len("NOT ")
                        else:
                            substr_for_edit = substr_for_edit.replace("NOT ", "")
                            substr_for_edit = substr_for_edit.replace(
                                substr_for_edit[1:],
                                f" {key} NOT ILIKE '%{substr_for_edit[1:]}%'",
                            )
                    else:
                        substr_for_edit = substr_for_edit.replace(
                            substr_for_edit[1:], f" {key} ILIKE '%{substr_for_edit[1:]}%'"
                        )

                    string = (
                        string[:start_ind]
                        + string[start_ind:lbnd_ind]
                        + substr_for_edit
                        + string[or_ind:]
                    )
                else:
                    next_ind = or_ind + 1
                next_sym = "OR"
            elif (
                br_c_ind == min(n for n in [and_ind, or_ind, br_c_ind] if n > 0)
                and br_c_ind > 0
            ):
                lbnd_br_o_ind = string.rfind("(", start_ind, br_c_ind)
                lbnd_br_c_ind = string.rfind(")", start_ind, br_c_ind)
                if lb_till_symb == "(":
                    lbnd_sym_ind = lbnd_br_o_ind
                elif lb_till_symb == ")":
                    lbnd_sym_ind = lbnd_br_c_ind
                elif lb_till_symb == "AND":
                    lbnd_sym_ind = string.rfind("AND", start_ind, br_c_ind) + 3
                elif lb_till_symb == "OR":
                    lbnd_sym_ind = string.rfind("OR", start_ind, br_c_ind) + 2
                lbnd_ind = max(lbnd_br_o_ind, lbnd_sym_ind)

                if string[start_ind:br_c_ind].replace(" ", "") != "":
                    next_ind = br_c_ind + 1 + add_sym_len
                    substr_for_edit = string[lbnd_ind:br_c_ind]

                    if (
                        "NOT " in substr_for_edit[1:]
                        and not "\\NOT " in substr_for_edit[1:]
                    ) or substr_for_edit[1:].startswith("-"):
                        if substr_for_edit[1:].startswith("-"):
                            substr_for_edit = substr_for_edit[0] + substr_for_edit[
                                2:
                            ].replace(
                                substr_for_edit[2:],
                                f" {key} NOT ILIKE '%{substr_for_edit[2:]}%'",
                            )
                            next_ind = next_ind - 1 + len("NOT ")
                        else:
                            substr_for_edit = substr_for_edit.replace("NOT ", "")
                            substr_for_edit = substr_for_edit.replace(
                                substr_for_edit[1:],
                                f" {key} NOT ILIKE '%{substr_for_edit[1:]}%'",
                            )
                    else:
                        substr_for_edit = substr_for_edit.replace(
                            substr_for_edit[1:], f" {key} ILIKE '%{substr_for_edit[1:]}%'"
                        )

                    string = (
                        string[:start_ind]
                        + string[start_ind:lbnd_ind]
                        + substr_for_edit
                        + string[br_c_ind:]
                    )
                else:
                    next_ind = br_c_ind + 1
                next_sym = ")"
        else:
            print(f'Converting initial query error: no AND, no OR, no ")" at the end! Incoming string: {string}')

        return string, next_ind, next_sym

    str_where_conditions = f"({init_query})"

    next_ind = 0
    next_sym = "("
    i = 1
    still_has_text_left = True
    while still_has_text_left:
        str_where_conditions, next_ind, next_sym = convert_part_to_where_cond(
            string=str_where_conditions,
            start_ind=next_ind,
            lb_till_symb=next_sym
        )
        if str_where_conditions[next_ind:].replace(")", "") == "":
            still_has_text_left = False
    
    return str_where_conditions


def convert_sql_where_to_qdrant_filters(sql_where_clause, res_type='json', make_lowercase=False):
    def parse_one_condition(condition, make_lowercase=False):
        match = re.match(r'^\(?\s*(\w+)\s*ILIKE\s*(.+)\s*\)?$', condition.strip())
        match_not = re.match(r'^\(?\s*(\w+)\s*NOT\s+ILIKE\s*(.+)\s*\)?$', condition.strip())
        if match:
            key, value = match.groups()
            return {"key": key, "not": False, "match": {"text": value.lower() if make_lowercase else value}}
        elif match_not:
            key, value = match_not.groups()
            return {"key": key, "not": True, "match": {"text": value.lower() if make_lowercase else value}}
        else:
            return None
    
    def get_lists_of_conditions(conditions, make_lowercase=False):
        stack = []
        current = []
        
        for cond in conditions:
            if cond == '(':
                stack.append(current)
                current = []
            elif cond == ')':
                last = current
                current = stack.pop()
                current.append(last)
            elif cond.upper() == 'AND':
                current.append('AND')
            elif cond.upper() == 'AND NOT':
                current.append('AND NOT')
            elif cond.upper() == 'OR':
                current.append('OR')
            elif cond.upper() == 'OR NOT':
                current.append('OR NOT')
            else:
                current.append(parse_one_condition(cond, make_lowercase=make_lowercase))
        
        return current

    def only_ors(lists_of_conds):
        res = {}
        should = []
        must_not = []
        
        for idx, item in enumerate(lists_of_conds):
            if item == 'OR NOT' and idx > 0 and idx < len(lists_of_conds) - 1:
                if isinstance(lists_of_conds[idx-1], dict):
                    if lists_of_conds[idx-1]['not']:
                        if lists_of_conds[idx-1] not in must_not:
                            must_not.append(lists_of_conds[idx-1])
                    else:
                        if lists_of_conds[idx-1] not in should and lists_of_conds[idx-1] not in must_not:
                            should.append(lists_of_conds[idx-1])
                elif isinstance(lists_of_conds[idx-1], list):
                    nested_res_left = make_qdrant_json_filters(lists_of_conds[idx-1])
                    if nested_res_left not in should and nested_res_left not in must_not:
                        should.append(nested_res_left)
                if isinstance(lists_of_conds[idx+1], dict):
                    if lists_of_conds[idx+1] not in must_not:
                        must_not.append(lists_of_conds[idx+1])
                elif isinstance(lists_of_conds[idx+1], list):
                    nested_res_right = make_qdrant_json_filters(lists_of_conds[idx+1])
                    if nested_res_right not in must_not:
                        must_not.append(nested_res_right)
    
        for idx, item in enumerate(lists_of_conds):
            if item == 'OR' and idx > 0 and idx < len(lists_of_conds) - 1:
                if isinstance(lists_of_conds[idx-1], dict):
                    if lists_of_conds[idx-1]['not']:
                        if lists_of_conds[idx-1] not in must_not:
                            must_not.append(lists_of_conds[idx-1])
                    else:
                        if lists_of_conds[idx-1] not in should and lists_of_conds[idx-1] not in must_not:
                            should.append(lists_of_conds[idx-1])
                elif isinstance(lists_of_conds[idx-1], list):
                    nested_res_left = make_qdrant_json_filters(lists_of_conds[idx-1])
                    if nested_res_left not in should and nested_res_left not in must_not:
                        should.append(nested_res_left)
                if isinstance(lists_of_conds[idx+1], dict):
                    if lists_of_conds[idx+1]['not']:
                        if lists_of_conds[idx+1] not in must_not:
                            must_not.append(lists_of_conds[idx+1])
                    else:
                        if lists_of_conds[idx+1] not in should:
                            should.append(lists_of_conds[idx+1])
                elif isinstance(lists_of_conds[idx+1], list):
                    nested_res_right = make_qdrant_json_filters(lists_of_conds[idx+1])
                    if nested_res_right not in should:
                        should.append(nested_res_right)
    
        if should:
            res["should"] = should
        else:
            res["should"] = []
        if must_not:
            for item in must_not:
                res["should"].append({"must_not": [item]})
        return res

    def only_ands(lists_of_conds):
        res = {}
        must = []
        must_not = []
        
        for idx, item in enumerate(lists_of_conds):
            if item == 'AND NOT' and idx > 0 and idx < len(lists_of_conds) - 1:
                if isinstance(lists_of_conds[idx-1], dict):
                    if lists_of_conds[idx-1]['not']:
                        if lists_of_conds[idx-1] not in must_not:
                            must_not.append(lists_of_conds[idx-1])
                    else:
                        if lists_of_conds[idx-1] not in must and lists_of_conds[idx-1] not in must_not:
                            must.append(lists_of_conds[idx-1])
                elif isinstance(lists_of_conds[idx-1], list):
                    nested_res_left = make_qdrant_json_filters(lists_of_conds[idx-1])
                    if nested_res_left not in must and nested_res_left not in must_not:
                        must.append(nested_res_left)
                
                if isinstance(lists_of_conds[idx+1], dict):
                    if lists_of_conds[idx+1] not in must_not:
                        must_not.append(lists_of_conds[idx+1])
                elif isinstance(lists_of_conds[idx+1], list):
                    nested_res_right = make_qdrant_json_filters(lists_of_conds[idx+1])
                    if nested_res_right not in must_not:
                        must_not.append(nested_res_right)
    
        for idx, item in enumerate(lists_of_conds):
            if item == 'AND' and idx > 0 and idx < len(lists_of_conds) - 1:
                if isinstance(lists_of_conds[idx-1], dict):
                    if lists_of_conds[idx-1]['not']:
                        if lists_of_conds[idx-1] not in must_not:
                            must_not.append(lists_of_conds[idx-1])
                    else:
                        if lists_of_conds[idx-1] not in must and lists_of_conds[idx-1] not in must_not:
                            must.append(lists_of_conds[idx-1])
                elif isinstance(lists_of_conds[idx-1], list):
                    nested_res_left = make_qdrant_json_filters(lists_of_conds[idx-1])
                    if nested_res_left not in must and nested_res_left not in must_not:
                        must.append(nested_res_left)
    
                if isinstance(lists_of_conds[idx+1], dict):
                    if lists_of_conds[idx+1]['not']:
                        if lists_of_conds[idx+1] not in must_not:
                            must_not.append(lists_of_conds[idx+1])
                    else:
                        if lists_of_conds[idx+1] not in must:
                            must.append(lists_of_conds[idx+1])
                elif isinstance(lists_of_conds[idx+1], list):
                    nested_res_right = make_qdrant_json_filters(lists_of_conds[idx+1])
                    if nested_res_right not in must:
                        must.append(nested_res_right)
        if must:
            res["must"] = must
        if must_not:
            res["must_not"] = must_not
        return res
    
    def both_ands_ors(lists_of_conds):
        res = {}
        ands_must = []
        ands_must_not = []
        ors_should = []
        ors_must_not = []
        ors_res = {}
        ands_res = {}
    
        for idx, item in enumerate(lists_of_conds):
            if item == 'AND NOT' and idx > 0 and idx < len(lists_of_conds) - 1:
                if isinstance(lists_of_conds[idx-1], dict):
                    if lists_of_conds[idx-1]['not']:
                        if lists_of_conds[idx-1] not in ands_must_not:
                            ands_must_not.append(lists_of_conds[idx-1])
                    else:
                        if lists_of_conds[idx-1] not in ands_must and lists_of_conds[idx-1] not in ands_must_not:
                            ands_must.append(lists_of_conds[idx-1])
                elif isinstance(lists_of_conds[idx-1], list):
                    nested_res_left = make_qdrant_json_filters(lists_of_conds[idx-1])
                    if nested_res_left not in ands_must and nested_res_left not in ands_must_not:
                        ands_must.append(nested_res_left)
                if isinstance(lists_of_conds[idx+1], dict):
                    if lists_of_conds[idx+1] not in ands_must_not:
                        ands_must_not.append(lists_of_conds[idx+1])
                elif isinstance(lists_of_conds[idx+1], list):
                    nested_res_right = make_qdrant_json_filters(lists_of_conds[idx+1])
                    if nested_res_right not in ands_must_not:
                        ands_must_not.append(nested_res_right)
    
        for idx, item in enumerate(lists_of_conds):
            if item == 'AND' and idx > 0 and idx < len(lists_of_conds) - 1:
                if isinstance(lists_of_conds[idx-1], dict):
                    if lists_of_conds[idx-1]['not']:
                        if lists_of_conds[idx-1] not in ands_must_not:
                            ands_must_not.append(lists_of_conds[idx-1])
                    else:
                        if lists_of_conds[idx-1] not in ands_must and lists_of_conds[idx-1] not in ands_must_not:
                            ands_must.append(lists_of_conds[idx-1])
                elif isinstance(lists_of_conds[idx-1], list):
                    nested_res_left = make_qdrant_json_filters(lists_of_conds[idx-1])
                    if nested_res_left not in ands_must and nested_res_left not in ands_must_not:
                        ands_must.append(nested_res_left)
                if isinstance(lists_of_conds[idx+1], dict):
                    if lists_of_conds[idx+1]['not']:
                        if lists_of_conds[idx+1] not in ands_must_not:
                            ands_must_not.append(lists_of_conds[idx+1])
                    else:
                        if lists_of_conds[idx+1] not in ands_must:
                            ands_must.append(lists_of_conds[idx+1])
                elif isinstance(lists_of_conds[idx+1], list):
                    nested_res_right = make_qdrant_json_filters(lists_of_conds[idx+1])
                    if nested_res_right not in ands_must:
                        ands_must.append(nested_res_right)
    
        for idx, item in enumerate(lists_of_conds):
            if item == 'OR NOT' and idx > 0 and idx < len(lists_of_conds) - 1:
                if isinstance(lists_of_conds[idx-1], dict):
                    if lists_of_conds[idx-1]['not']:
                        if lists_of_conds[idx-1] not in ors_must_not and lists_of_conds[idx-1] not in ands_must_not:
                            ors_must_not.append(lists_of_conds[idx-1])
                    else:
                        if lists_of_conds[idx-1] not in ors_should and lists_of_conds[idx-1] not in ands_must and lists_of_conds[idx-1] not in ands_must_not:
                            ors_should.append(lists_of_conds[idx-1])
                elif isinstance(lists_of_conds[idx-1], list):
                    nested_res_left = make_qdrant_json_filters(lists_of_conds[idx-1])
                    if nested_res_left not in ors_should and nested_res_left not in ands_must and nested_res_left not in ands_must_not:
                        ors_should.append(nested_res_left)
                if isinstance(lists_of_conds[idx+1], dict):
                    if lists_of_conds[idx+1] not in ors_must_not and lists_of_conds[idx+1] not in ands_must and lists_of_conds[idx+1] not in ands_must_not:
                        ors_must_not.append(lists_of_conds[idx+1])
                elif isinstance(lists_of_conds[idx+1], list):
                    nested_res_right = make_qdrant_json_filters(lists_of_conds[idx+1])
                    if nested_res_right not in ors_must_not and nested_res_right not in ands_must and nested_res_right not in ands_must_not:
                        ors_must_not.append(nested_res_right)
                        
        for idx, item in enumerate(lists_of_conds):
            if item == 'OR' and idx > 0 and idx < len(lists_of_conds) - 1:
                if isinstance(lists_of_conds[idx-1], dict):
                    if lists_of_conds[idx-1]['not']:
                        if lists_of_conds[idx-1] not in ors_must_not and lists_of_conds[idx-1] not in ands_must_not:
                            ors_must_not.append(lists_of_conds[idx-1])
                    else:
                        if lists_of_conds[idx-1] not in ors_should and lists_of_conds[idx-1] not in ors_must_not and lists_of_conds[idx-1] not in ands_must and lists_of_conds[idx-1] not in ands_must_not:
                            ors_should.append(lists_of_conds[idx-1])
                elif isinstance(lists_of_conds[idx-1], list):
                    nested_res_left = make_qdrant_json_filters(lists_of_conds[idx-1])
                    if nested_res_left not in ors_should and nested_res_left not in ors_must_not and nested_res_left not in ands_must and nested_res_left not in ands_must_not:
                        ors_should.append(lists_of_conds[idx-1])
                if isinstance(lists_of_conds[idx+1], dict):
                    if lists_of_conds[idx+1]['not']:
                        if lists_of_conds[idx+1] not in ors_must_not and lists_of_conds[idx+1] not in ands_must_not:
                            ors_must_not.append(lists_of_conds[idx+1])
                    else:
                        if lists_of_conds[idx+1] not in ors_should and lists_of_conds[idx+1] not in ands_must and lists_of_conds[idx+1] not in ands_must_not:
                            ors_should.append(lists_of_conds[idx+1])
                elif isinstance(lists_of_conds[idx+1], list):
                    nested_res_right = make_qdrant_json_filters(lists_of_conds[idx+1])
                    if nested_res_right not in ors_should and nested_res_right not in ands_must and nested_res_right not in ands_must_not:
                        ors_should.append(lists_of_conds[idx+1])
    
        if ors_should:
            ors_res["should"] = ors_should
        else:
            ors_res["should"] = []
        if ors_must_not:
            for item in ors_must_not:
                ors_res["should"].append({"must_not": [item]})
        
        res = {"should": ors_res["should"]}
        if ands_must:
            ands_res["must"] = ands_must
        if ands_must_not:
            ands_res["must_not"] = ands_must_not
        if ands_res:
            res['should'].append(ands_res)
    
        return res
    
    def make_qdrant_json_filters(lists_of_conds):
        res = {}
        # CASE Only ORs --------------------------------------------------
        if all(x in ['OR', 'OR NOT'] for x in lists_of_conds if isinstance(x, str)):
            res = only_ors(lists_of_conds)
        # CASE Only ANDs --------------------------------------------------------------
        if all(x in ['AND', 'AND NOT'] for x in lists_of_conds if isinstance(x, str)):
            res = only_ands(lists_of_conds)
        # CASE Both ORs and ANDs -----------------------------------------------------------------------------
        if ('OR' in lists_of_conds or 'OR NOT' in lists_of_conds) and ('AND' in lists_of_conds or 'AND NOT' in lists_of_conds):
            res = both_ands_ors(lists_of_conds)
        # CASE with only 1 condition
        if not 'OR' in lists_of_conds and not 'OR NOT' in lists_of_conds and not 'AND' in lists_of_conds and not 'AND NOT' in lists_of_conds and len(lists_of_conds) == 1:
            res['must'] = [lists_of_conds[0]]
        return res
    
    def convert_qdrant_json_to_qdrant_models_filters(json_filters):
        res = models.Filter()
        if isinstance(json_filters, dict):
            for rule in json_filters:
                if rule == 'should':
                    res.should = []
                    for item in json_filters[rule]:
                        if isinstance(item, dict) and 'key' in item.keys():
                            res.should.append(models.FieldCondition(
                                key=item['key'],
                                match=models.MatchText(text=item['match']['text']),
                            ))
                        elif isinstance(item, dict) and ('should' in item.keys() or 'must' in item.keys() or 'must_not' in item.keys()):
                            nested_res = convert_qdrant_json_to_qdrant_models_filters(item)
                            res.should.append(nested_res)
                elif rule == 'must':
                    res.must = []
                    for item in json_filters[rule]:
                        if isinstance(item, dict) and 'key' in item.keys():
                            res.must.append(models.FieldCondition(
                                key=item['key'],
                                match=models.MatchText(text=item['match']['text']),
                            ))
                        elif isinstance(item, dict) and ('should' in item.keys() or 'must' in item.keys() or 'must_not' in item.keys()):
                            nested_res = convert_qdrant_json_to_qdrant_models_filters(item)
                            res.must.append(nested_res)
                elif rule == 'must_not':
                    res.must_not = []
                    for item in json_filters[rule]:
                        if isinstance(item, dict) and 'key' in item.keys():
                            res.must_not.append(models.FieldCondition(
                                key=item['key'],
                                match=models.MatchText(text=item['match']['text']),
                            ))
                        elif isinstance(item, dict) and ('should' in item.keys() or 'must' in item.keys() or 'must_not' in item.keys()):
                            nested_res = convert_qdrant_json_to_qdrant_models_filters(item)
                            res.must_not.append(nested_res)
        return res
    
    clean_query = sql_where_clause.replace("'%",'').replace("%'",'')
    if clean_query.startswith('(') and clean_query.endswith(')'):
        clean_query = clean_query[1:-1]

    conditions = re.split(r'(\s+AND\s+NOT\s+|\s+OR\s+NOT\s+|\s+AND\s+|\s+OR\s+|\(|\))', clean_query)
    conditions = [cond.strip() for cond in conditions if cond.strip()]

    for idx, cond in enumerate(conditions):
        if (cond.startswith('AND') or cond.startswith('OR')) and cond.endswith('NOT'):
            conditions[idx] = ' '.join(cond.split()) # it's for case text ILIKE '%apple%' OR     NOT text ILIKE '%ornage%' just to remove useless spaces instead of 1 space - we will use later RegExp match with exact 1 space to catch "OR NOT", "AND NOT" in get_lists_of_conditions func
    
    lists_of_conditions = get_lists_of_conditions(conditions, make_lowercase=make_lowercase)
    qdrant_json_filters = make_qdrant_json_filters(lists_of_conditions)
    if res_type == 'json':
        return qdrant_json_filters
    else:
        qdrant_models_filters = convert_qdrant_json_to_qdrant_models_filters(qdrant_json_filters)
        return qdrant_models_filters


if __name__ == '__main__':
    sql_table = 'posts'
    qdrant_collection = 'my_collection'
    key = 'text'

    client_qdr = QdrantClient(url="http://localhost:6333")
    is_collection_exist = client_qdr.collection_exists(collection_name=qdrant_collection)
    if not is_collection_exist:
        client_qdr.create_collection(
            collection_name=qdrant_collection,
            vectors_config=VectorParams(size=4, distance=Distance.DOT),
        )
    first_data_insert = client_qdr.upsert(
        collection_name=qdrant_collection,
        wait=True,
        points=[
            PointStruct(id=1, vector=[0.05, 0.61, 0.76, 0.74], payload={"text": "green apples with yellow lemons"}),
            PointStruct(id=2, vector=[0.19, 0.81, 0.75, 0.11], payload={"text": "mint and tomatos are the same"}),
            PointStruct(id=3, vector=[0.36, 0.55, 0.47, 0.94], payload={"text": "oranges with apples are like lemons"}),
            PointStruct(id=4, vector=[0.18, 0.01, 0.85, 0.80], payload={"text": "potato is just mint above oranges"}),
            PointStruct(id=5, vector=[0.24, 0.18, 0.22, 0.44], payload={"text": "apples are almost tomatos"}),
            PointStruct(id=6, vector=[0.35, 0.08, 0.11, 0.44], payload={"text": "apples, oranges, lemons, tomatos, mint, potato - all"}),
        ],
    )
    print('First data insert to Qdrant DB status:\n', first_data_insert)

    init_queries = [
        'apples AND oranges', # answer ids: 3,6
        'tomatos OR mint', # answer ids: 2,4,5,6
        'apples AND oranges AND NOT tomatos', # answer ids: 3
        'all OR (oranges AND mint)', # answer ids: 4,6
        'apples AND (NOT tomatos OR lemons) AND (oranges AND NOT mint)',  # answer ids: 3
        '(apples AND oranges) OR (tomatos AND (lemons OR mint))', # answer ids: 2,3,6
        'oranges AND (NOT lemons OR potato) AND (mint AND NOT (apples OR tomatos))', # answer ids: 4
        'apples AND NOT all AND (lemons OR potato OR (oranges AND NOT (tomatos OR mint)))' # answer ids: 1,3
    ]

    for init_query in init_queries:
        print('='*50, f'\nInitial query:\n{init_query}')

        str_where_clause = convert_init_query_to_proper_sql_where_clause(init_query=init_query, key=key)
        sql_query_string = f"SELECT * FROM {sql_table} WHERE {str_where_clause}"
        print(f'SQL with proper WHERE clause:\n{sql_query_string}')

        qdrant_json_filters = convert_sql_where_to_qdrant_filters(str_where_clause, res_type='json', make_lowercase=True)
        print('Qdrant filetrs in JSON format:\n', json.dumps(qdrant_json_filters, indent=4))

        qdrant_models_filters =  convert_sql_where_to_qdrant_filters(str_where_clause, res_type='models', make_lowercase=True)
        print('Qdrant filetrs in Models format:\n',qdrant_models_filters.__repr__())
        
        res = client_qdr.scroll(
            collection_name=qdrant_collection,
            scroll_filter=qdrant_models_filters
        )
        print('Res of select from Qdrant DB by filters:')
        for document in res[0]:
            document_dict = document.__dict__
            print(f"id={document.id}: {document.payload['text']}")
        