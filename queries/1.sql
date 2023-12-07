select
    l_returnflag,
    sum(case
        when o_shippriority between 1 and 2
            then 1
        else 0
    end) as high_priority_count,
    sum(case
        when o_shippriority not between 1 and 2
            then 1
        else 0
    end) as low_priority_count
from
    orders,
    lineitem
where
    o_orderkey = l_orderkey
    and o_totalprice < 20000
    and l_extendedprice > 3000
group by
    l_returnflag
order by
    l_returnflag;