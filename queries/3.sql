select
    o_orderpriority,
    count(*) as order_count
from
    orders
join
    lineitem on o_orderkey = l_orderkey
where
    o_totalprice > 3000
group by
    o_orderpriority
order by
    o_orderpriority;