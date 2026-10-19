from datetime import date, datetime, timezone, timedelta
import pytest
from src.tracking import daily_series, windows
from src.live_showcase import data_model

def series(days=60):
    end=date(2026,10,18)
    return {(end-timedelta(days=i)).isoformat():float(100 if i<30 else 50) for i in range(days)},end

def test_complete_windows_use_previous_nonoverlapping_period():
    s,end=series()
    result=windows(s,end)
    assert result['30']['current']==3000
    assert result['30']['previous']==1500
    assert result['30']['change_pct']==100
    assert result['7']['change_pct']==0

def test_missing_day_is_not_interpolated_or_zero_filled():
    s,end=series()
    del s[(end-timedelta(days=3)).isoformat()]
    result=windows(s,end)
    assert result['7']['current'] is None
    assert result['7']['change_pct'] is None
    assert result['1']['current']==100

def test_today_partial_and_null_points_are_excluded():
    stamp=lambda d:int(datetime(2026,10,d,tzinfo=timezone.utc).timestamp())
    s=daily_series([[stamp(17),1],[stamp(18),None],[stamp(19),999999]],date(2026,10,19))
    assert s=={'2026-10-17':1.0}

def test_zero_prior_does_not_produce_infinite_growth():
    assert windows({'2026-10-18':1,'2026-10-17':0},date(2026,10,18))['1']['change_pct'] is None

def test_refuse_old_data_and_blank_operating_observations():
    snapshot={'timestamp':'2026-01-01T00:00:00+00:00','volume_24h':1}
    with pytest.raises(ValueError,match='old snapshot'):
        data_model({'snapshots':{'Hyperliquid':snapshot,'Aster':snapshot}}, {})
    with pytest.raises(ValueError,match='no operating data'):
        data_model({'snapshots':{'Hyperliquid':{'timestamp':datetime.now(timezone.utc).isoformat()}}}, {})

def test_missing_one_protocol_does_not_become_zero_share():
    h={'timestamp':datetime.now(timezone.utc).isoformat(),'volume_24h':1}
    a={'timestamp':h['timestamp'],'fees_24h':1}
    data=data_model({'snapshots':{'Hyperliquid':h,'Aster':a}}, {})
    assert data['shares']['volume']=={'hyperliquid':None,'aster':None}
