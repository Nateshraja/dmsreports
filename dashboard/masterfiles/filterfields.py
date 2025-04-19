from django.http import JsonResponse
from django.db import connection
import logging

logger = logging.getLogger(__name__)

def execute_query(query, params=None):
    """
    Helper function to execute a query and return the results.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params or [])
            return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"Error executing query: {query} - {e}")
        raise e


def get_group1_dropdown_options(request):
    code = request.session.get('param1')
    type_param = request.session.get('param2')

    if not type_param:
        return JsonResponse({'error': 'Missing session parameter: param2'}, status=400)

    try:
        if type_param == 'Ramraj':
            query = """select distinct pt2.group1  from res_company rc 
                inner join product_template_res_company_rel pt on pt.res_company_id  = rc.id 
                inner join product_template pt2 on pt.product_template_id = pt2.id
                where pt2.type <> 'service' """
            options = execute_query(query)
        elif type_param == 'Distributor':
            if not code:
                return JsonResponse({'error': 'Missing session parameter: param1'}, status=400)
            query = """select distinct pt2.group1  from res_company rc 
                inner join product_template_res_company_rel pt on pt.res_company_id  = rc.id 
                inner join product_template pt2 on pt.product_template_id = pt2.id
                where pt2.type <> 'service' and rc.distributor_code = %s """
            options = execute_query(query, [code])
        else:
            return JsonResponse({'error': f'Invalid type_param: {type_param}'}, status=400)

        return JsonResponse({'options': options}, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_group2_dropdown_options(request):
    code = request.session.get('param1')
    type_param = request.session.get('param2')

    if not type_param:
        return JsonResponse({'error': 'Missing session parameter: param2'}, status=400)

    try:
        if type_param == 'Ramraj':
            query = """select distinct pt2.group2  from res_company rc 
                inner join product_template_res_company_rel pt on pt.res_company_id  = rc.id 
                inner join product_template pt2 on pt.product_template_id = pt2.id
                where pt2.type <> 'service' """
            options = execute_query(query)
        elif type_param == 'Distributor':
            if not code:
                return JsonResponse({'error': 'Missing session parameter: param1'}, status=400)
            query = """select distinct pt2.group2  from res_company rc 
                inner join product_template_res_company_rel pt on pt.res_company_id  = rc.id 
                inner join product_template pt2 on pt.product_template_id = pt2.id
                where pt2.type <> 'service' and rc.distributor_code = %s  """
            options = execute_query(query, [code])
        else:
            return JsonResponse({'error': f'Invalid type_param: {type_param}'}, status=400)

        return JsonResponse({'options': options}, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_distributor_dropdown_options(request):
    code = request.session.get('param1')
    type_param = request.session.get('param2')

    if not type_param:
        return JsonResponse({'error': 'Missing session parameter: param2'}, status=400)

    try:
        if type_param == 'Ramraj':
            query = """SELECT DISTINCT distributor_name FROM public."sales_invoice_BI" """
            options = execute_query(query)
        elif type_param == 'Distributor':
            if not code:
                return JsonResponse({'error': 'Missing session parameter: param1'}, status=400)
            query = """
                SELECT DISTINCT distributor_name
                FROM public."sales_invoice_BI"
                WHERE distributor_code = %s
            """
            options = execute_query(query, [code])
        else:
            return JsonResponse({'error': f'Invalid type_param: {type_param}'}, status=400)

        return JsonResponse({'options': options}, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_current_state(request):
    code = request.session.get('param1')
    type_param = request.session.get('param2')
    if not type_param:
        return JsonResponse({'error': 'Missing session parameter: param2'}, status=400)

    try:
        if type_param == 'Ramraj':
            query = """SELECT state_code state
            FROM res_company
            WHERE distributor_code = %s """
            options = execute_query(query, [code])
        elif type_param == 'Distributor':
            if not code:
                return JsonResponse({'error': 'Missing session parameter: param1'}, status=400)
            query = """
                SELECT state_code state
            FROM res_company
            WHERE distributor_code = %s
            """
            options = execute_query(query, [code])
        else:
            return JsonResponse({'error': f'Invalid type_param: {type_param}'}, status=400)
        return JsonResponse({'options': options}, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_product_distributor_dropdown_options(request):
    code = request.session.get('param1')
    type_param = request.session.get('param2')

    if not type_param:
        return JsonResponse({'error': 'Missing session parameter: param2'}, status=400)

    try:
        if type_param == 'Ramraj':
            query = """select distinct rc.name distributor  from res_company rc 
                inner join product_template_res_company_rel pt on pt.res_company_id  = rc.id 
                inner join product_template pt2 on pt.product_template_id = pt2.id
                where pt2.type <> 'service' """
            options = execute_query(query)
        elif type_param == 'Distributor':
            if not code:
                return JsonResponse({'error': 'Missing session parameter: param1'}, status=400)
            query = """select distinct rc.name distributor  from res_company rc 
                inner join product_template_res_company_rel pt on pt.res_company_id  = rc.id 
                inner join product_template pt2 on pt.product_template_id = pt2.id
                where pt2.type <> 'service' and rc.distributor_code = %s  """
            options = execute_query(query, [code])
            print(options)
        else:
            return JsonResponse({'error': f'Invalid type_param: {type_param}'}, status=400)

        return JsonResponse({'options': options}, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_product_dropdown_options(request):
    code = request.session.get('param1')
    type_param = request.session.get('param2')

    if not type_param:
        return JsonResponse({'error': 'Missing session parameter: param2'}, status=400)

    try:
        if type_param == 'Ramraj':
            query = """select distinct pt2.name->>'en_US' product  from res_company rc 
                inner join product_template_res_company_rel pt on pt.res_company_id  = rc.id 
                inner join product_template pt2 on pt.product_template_id = pt2.id
                where pt2.type <> 'service' """
            options = execute_query(query)
        elif type_param == 'Distributor':
            if not code:
                return JsonResponse({'error': 'Missing session parameter: param1'}, status=400)
            query = """select distinct pt2.name->>'en_US' product  from res_company rc 
                inner join product_template_res_company_rel pt on pt.res_company_id  = rc.id 
                inner join product_template pt2 on pt.product_template_id = pt2.id
                where pt2.type <> 'service' and rc.distributor_code = %s  """
            options = execute_query(query, [code])
        else:
            return JsonResponse({'error': f'Invalid type_param: {type_param}'}, status=400)

        return JsonResponse({'options': options}, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_product_category_dropdown_options(request):
    code = request.session.get('param1')
    type_param = request.session.get('param2')

    if not type_param:
        return JsonResponse({'error': 'Missing session parameter: param2'}, status=400)

    try:
        if type_param == 'Ramraj':
            query = """select distinct pc."name" category  from res_company rc 
                inner join product_template_res_company_rel pt on pt.res_company_id  = rc.id 
                inner join product_template pt2 on pt.product_template_id = pt2.id
                inner JOIN product_category pc ON pt2.categ_id = pc.id
                where pt2.type <> 'service' """
            options = execute_query(query)
        elif type_param == 'Distributor':
            if not code:
                return JsonResponse({'error': 'Missing session parameter: param1'}, status=400)
            query = """select distinct pc."name" category  from res_company rc 
                inner join product_template_res_company_rel pt on pt.res_company_id  = rc.id 
                inner join product_template pt2 on pt.product_template_id = pt2.id
                inner JOIN product_category pc ON pt2.categ_id = pc.id
                where pt2.type <> 'service' and rc.distributor_code = %s  """
            options = execute_query(query, [code])
        else:
            return JsonResponse({'error': f'Invalid type_param: {type_param}'}, status=400)

        return JsonResponse({'options': options}, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_product_division_dropdown_options(request):
    code = request.session.get('param1')
    type_param = request.session.get('param2')

    if not type_param:
        return JsonResponse({'error': 'Missing session parameter: param2'}, status=400)

    try:
        if type_param == 'Ramraj':
            query = """select distinct cd.division_code division  from res_company rc 
                inner join product_template_res_company_rel pt on pt.res_company_id  = rc.id 
                inner join product_template pt2 on pt.product_template_id = pt2.id
                inner join res_partner cd ON pt2.division_id = cd.id
                where pt2.type <> 'service' """
            options = execute_query(query)
        elif type_param == 'Distributor':
            if not code:
                return JsonResponse({'error': 'Missing session parameter: param1'}, status=400)
            query = """select distinct cd.division_code division  from res_company rc 
                inner join product_template_res_company_rel pt on pt.res_company_id  = rc.id 
                inner join product_template pt2 on pt.product_template_id = pt2.id
                inner join res_partner cd ON pt2.division_id = cd.id
                where pt2.type <> 'service' and rc.distributor_code = %s  """
            options = execute_query(query, [code])
        else:
            return JsonResponse({'error': f'Invalid type_param: {type_param}'}, status=400)

        return JsonResponse({'options': options}, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_product_brand_dropdown_options(request):
    code = request.session.get('param1')
    type_param = request.session.get('param2')

    if not type_param:
        return JsonResponse({'error': 'Missing session parameter: param2'}, status=400)

    try:
        if type_param == 'Ramraj':
            query = """select distinct br."name" brand  from res_company rc 
                inner join product_template_res_company_rel pt on pt.res_company_id  = rc.id 
                inner join product_template pt2 on pt.product_template_id = pt2.id
                inner JOIN brand br ON pt2.brand_id = br.id
                where pt2.type <> 'service' """
            options = execute_query(query)
        elif type_param == 'Distributor':
            if not code:
                return JsonResponse({'error': 'Missing session parameter: param1'}, status=400)
            query = """select distinct br."name" brand  from res_company rc 
                inner join product_template_res_company_rel pt on pt.res_company_id  = rc.id 
                inner join product_template pt2 on pt.product_template_id = pt2.id
                inner JOIN brand br ON pt2.brand_id = br.id
                where pt2.type <> 'service' and rc.distributor_code = %s  """
            options = execute_query(query, [code])
        else:
            return JsonResponse({'error': f'Invalid type_param: {type_param}'}, status=400)

        return JsonResponse({'options': options}, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_product_state_dropdown_options(request):
    code = request.session.get('param1')
    type_param = request.session.get('param2')

    if not type_param:
        return JsonResponse({'error': 'Missing session parameter: param2'}, status=400)

    try:
        if type_param == 'Ramraj':
            query = """select distinct rc.state_code state  from res_company rc 
                inner join product_template_res_company_rel pt on pt.res_company_id  = rc.id 
                inner join product_template pt2 on pt.product_template_id = pt2.id
                inner JOIN brand br ON pt2.brand_id = br.id
                where pt2.type <> 'service' """
            options = execute_query(query)
        elif type_param == 'Distributor':
            if not code:
                return JsonResponse({'error': 'Missing session parameter: param1'}, status=400)
            query = """select distinct rc.state_code state  from res_company rc 
                inner join product_template_res_company_rel pt on pt.res_company_id  = rc.id 
                inner join product_template pt2 on pt.product_template_id = pt2.id
                inner JOIN brand br ON pt2.brand_id = br.id
                where pt2.type <> 'service' and rc.distributor_code = %s  """
            options = execute_query(query, [code])
        else:
            return JsonResponse({'error': f'Invalid type_param: {type_param}'}, status=400)

        return JsonResponse({'options': options}, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

'''def get_current_state_dropdown_options(request):
    code = request.session.get('param1')
    type_param = request.session.get('param2')

    if not type_param:
        return JsonResponse({'error': 'Missing session parameter: param2'}, status=400)

    try:
        if not code:
            return JsonResponse({'error': 'Missing session parameter: param1'}, status=400)
        query = """select distinct rc.state_code state  from res_company rc 
            inner join product_template_res_company_rel pt on pt.res_company_id  = rc.id 
            inner join product_template pt2 on pt.product_template_id = pt2.id
            inner JOIN brand br ON pt2.brand_id = br.id
            where pt2.type <> 'service' and rc.distributor_code = %s  """
        options = execute_query(query, [code])
        return JsonResponse({'options': options}, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)'''

def execute_query1(query, params=None):
    """
    Helper function to execute a query and return all columns from the results.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params or [])
            return cursor.fetchall()  # Return all rows with all columns
    except Exception as e:
        logger.error(f"Error executing query: {query} - {e}")
        raise e

def get_stock_report_dropdown_options(request):
    code = request.session.get('param1')
    type_param = request.session.get('param2')

    if not type_param:
        return JsonResponse({'error': 'Missing session parameter: param2'}, status=400)

    try:
        if type_param == 'Ramraj':
            query = """select distinct rc.id, rc.state_code, rc."name" dist_name, rc.distributor_code, cd.division_code division,
                        pt2.division_id divi_id, pc."name" category, pc.id categ_id, br."name" brand,
                        br.id brnd_id, pt2."name"->>'en_US' product, pt2.id prod_tmp_id, pp.product_variant_name,
                        pp.rr_item, pp.id prod_id, uu.ratio, coalesce(pp.standard_cost, 0) standard_cost, cdt.discount,
                        coalesce(pp.standard_cost, 0)*uu.ratio unit_cost
                        from res_company rc
                        inner join company_discount cdt ON rc.id = cdt.company_id
                        inner join product_template_res_company_rel pt on pt.res_company_id = rc.id
                        inner join product_template pt2 on pt.product_template_id = pt2.id
                        inner join product_product pp on pt2.id = pp.product_tmpl_id
                        inner JOIN product_category pc ON pt2.categ_id = pc.id
                        inner join res_partner cd ON pt2.division_id = cd.id
                        inner JOIN brand br ON pt2.brand_id = br.id
                        inner JOIN ( SELECT x.id, x.ratio::numeric AS ratio
                                    FROM ( SELECT uom_uom.id,
                                                  CASE
                                                      WHEN split_part(uom_uom.name ->> 'en_US'::text, '-', 1) = 'Dozens' THEN '12'
                                                      WHEN split_part(uom_uom.name ->> 'en_US'::text, '-', 1) = 'Units' THEN '1'
                                                      ELSE split_part(uom_uom.name ->> 'en_US'::text, '-', 2)
                                                  END AS ratio
                                           FROM uom_uom) x
                                    WHERE x.ratio <> '') uu ON pt2.uom_id = uu.id
                        where 1=1"""
            options = execute_query1(query)

        elif type_param == 'Distributor':
            if not code:
                return JsonResponse({'error': 'Missing session parameter: param1'}, status=400)

            query = """select distinct rc.id, rc.state_code, rc."name" dist_name, rc.distributor_code, cd.division_code division,
                        pt2.division_id divi_id, pc."name" category, pc.id categ_id, br."name" brand,
                        br.id brnd_id, pt2."name"->>'en_US' product, pt2.id prod_tmp_id, pp.product_variant_name,
                        pp.rr_item, pp.id prod_id, uu.ratio, coalesce(pp.standard_cost, 0) standard_cost, cdt.discount,
                        coalesce(pp.standard_cost, 0)*uu.ratio unit_cost
                        from res_company rc
                        inner join company_discount cdt ON rc.id = cdt.company_id
                        inner join product_template_res_company_rel pt on pt.res_company_id = rc.id
                        inner join product_template pt2 on pt.product_template_id = pt2.id
                        inner join product_product pp on pt2.id = pp.product_tmpl_id
                        inner JOIN product_category pc ON pt2.categ_id = pc.id
                        inner join res_partner cd ON pt2.division_id = cd.id
                        inner JOIN brand br ON pt2.brand_id = br.id
                        inner JOIN ( SELECT x.id, x.ratio::numeric AS ratio
                                    FROM ( SELECT uom_uom.id,
                                                  CASE
                                                      WHEN split_part(uom_uom.name ->> 'en_US'::text, '-', 1) = 'Dozens' THEN '12'
                                                      WHEN split_part(uom_uom.name ->> 'en_US'::text, '-', 1) = 'Units' THEN '1'
                                                      ELSE split_part(uom_uom.name ->> 'en_US'::text, '-', 2)
                                                  END AS ratio
                                           FROM uom_uom) x
                                    WHERE x.ratio <> '') uu ON pt2.uom_id = uu.id
                        where rc.distributor_code = %s"""
            options = execute_query1(query, [code])
            #print(options)

        else:
            return JsonResponse({'error': f'Invalid type_param: {type_param}'}, status=400)

        # If needed, you can format the result here before returning it
        formatted_options = [{"state_code": row[1], "dist_name": row[2], "division": row[5], "category": row[7], "brand": row[9], "product": row[10]} for row in options]

        return JsonResponse({'options': formatted_options}, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

