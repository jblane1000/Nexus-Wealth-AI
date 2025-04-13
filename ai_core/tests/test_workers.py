import pytest

# Assuming pytest-asyncio is installed for async tests

from ai_core.worker_ai.equity import EquityWorker
from ai_core.worker_ai.crypto import CryptoWorker
from ai_core.worker_ai.risk import RiskWorker

# --- Equity Worker Tests ---

@pytest.fixture
def equity_worker():
    """Fixture to create an EquityWorker instance for tests."""
    config = {'brokerage_api_key': 'dummy_equity_broker', 'market_data_api_key': 'dummy_equity_data'}
    return EquityWorker(worker_id='test_equity_01', mcu_endpoint='dummy_mcu', config=config)

@pytest.mark.asyncio
async def test_equity_worker_trade_task(equity_worker):
    """Test EquityWorker handling a valid trade task."""
    task_data = {'action': 'BUY', 'symbol': 'AAPL', 'quantity': 10}
    result = await equity_worker.perform_task(task_type='equity_trade', task_data=task_data)
    assert result['status'] == 'success'
    assert 'confirmation_id' in result
    assert 'Simulated execution' in result['message']
    assert 'AAPL' in result['message']

@pytest.mark.asyncio
async def test_equity_worker_analysis_task(equity_worker):
    """Test EquityWorker handling a valid analysis task."""
    task_data = {'symbol': 'MSFT', 'current_price': 300}
    result = await equity_worker.perform_task(task_type='equity_analysis', task_data=task_data)
    assert result['status'] == 'success'
    assert result['symbol'] == 'MSFT'
    assert 'analysis' in result
    assert result['analysis']['recommendation'] == 'Hold'

@pytest.mark.asyncio
async def test_equity_worker_unsupported_task(equity_worker):
    """Test EquityWorker handling an unsupported task type."""
    result = await equity_worker.perform_task(task_type='unknown_task', task_data={})
    assert result['status'] == 'failed'
    assert 'Unsupported task type' in result['error']

# --- Crypto Worker Tests ---

@pytest.fixture
def crypto_worker():
    """Fixture to create a CryptoWorker instance for tests."""
    config = {'crypto_exchange_api_key': 'dummy_crypto_exchange', 'crypto_data_api_key': 'dummy_crypto_data'}
    return CryptoWorker(worker_id='test_crypto_01', mcu_endpoint='dummy_mcu', config=config)

@pytest.mark.asyncio
async def test_crypto_worker_trade_task(crypto_worker):
    """Test CryptoWorker handling a valid trade task."""
    task_data = {'action': 'SELL', 'symbol': 'BTC', 'quantity': 0.5}
    result = await crypto_worker.perform_task(task_type='crypto_trade', task_data=task_data)
    assert result['status'] == 'success'
    assert 'confirmation_id' in result
    assert 'Simulated execution' in result['message']
    assert 'BTC' in result['message']

@pytest.mark.asyncio
async def test_crypto_worker_analysis_task(crypto_worker):
    """Test CryptoWorker handling a valid analysis task."""
    task_data = {'symbol': 'ETH'}
    result = await crypto_worker.perform_task(task_type='crypto_analysis', task_data=task_data)
    assert result['status'] == 'success'
    assert result['symbol'] == 'ETH'
    assert 'analysis' in result
    assert result['analysis']['sentiment'] == 'Neutral'

@pytest.mark.asyncio
async def test_crypto_worker_unsupported_task(crypto_worker):
    """Test CryptoWorker handling an unsupported task type."""
    result = await crypto_worker.perform_task(task_type='defi_magic', task_data={})
    assert result['status'] == 'failed'
    assert 'Unsupported task type' in result['error']

# --- Risk Worker Tests ---

@pytest.fixture
def risk_worker():
    """Fixture to create a RiskWorker instance for tests."""
    config = {'risk_models': ['model1.pkl', 'model2.joblib']}
    return RiskWorker(worker_id='test_risk_01', mcu_endpoint='dummy_mcu', config=config)

@pytest.mark.asyncio
async def test_risk_worker_var_task(risk_worker):
    """Test RiskWorker handling a valid VaR calculation task."""
    task_data = {'portfolio_value': 500000, 'confidence_level': 0.99}
    result = await risk_worker.perform_task(task_type='calculate_var', task_data=task_data)
    assert result['status'] == 'success'
    assert 'value_at_risk' in result
    assert result['value_at_risk']['confidence_level'] == 0.99
    assert result['value_at_risk']['amount'] > 0

@pytest.mark.asyncio
async def test_risk_worker_stress_test_task(risk_worker):
    """Test RiskWorker handling a valid stress test task."""
    task_data = {'portfolio_value': 250000, 'scenario': 'Interest Rate Hike'}
    result = await risk_worker.perform_task(task_type='stress_test', task_data=task_data)
    assert result['status'] == 'success'
    assert result['scenario'] == 'Interest Rate Hike'
    assert 'estimated_impact' in result
    assert result['estimated_impact'] < 0 # Expecting a loss

@pytest.mark.asyncio
async def test_risk_worker_unsupported_task(risk_worker):
    """Test RiskWorker handling an unsupported task type."""
    result = await risk_worker.perform_task(task_type='predict_future', task_data={})
    assert result['status'] == 'failed'
    assert 'Unsupported task type' in result['error']
