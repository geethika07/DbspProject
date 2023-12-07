select
    l_returnflag,
    l_linestatus,
    sum(l_quantity) as total_qty,
    sum(l_extendedprice) as total_base_price,
    sum(l_extendedprice * (1 - l_discount)) as total_discounted_price,
    sum(l_extendedprice * (1 - l_discount) * (1 + l_tax)) as total_price_with_tax,
    avg(l_quantity) as average_qty,
    avg(l_extendedprice) as average_price,
    avg(l_discount) as average_discount_rate,
    count(*) as total_orders
from
    lineitem
where
    l_extendedprice < 33000
group by
    l_returnflag, l_linestatus
order by
    l_returnflag, l_linestatus;