// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../src/QEV124BaseFork.sol";

interface VmV124 {
    function createSelectFork(string calldata rpcUrl) external returns (uint256 forkId);
    function deal(address who, uint256 newBalance) external;
    function snapshotState() external returns (uint256 snapshotId);
    function revertToState(uint256 snapshotId) external returns (bool success);
}

contract QEV124BaseForkTest {
    VmV124 internal constant vm = VmV124(address(uint160(uint256(keccak256("hevm cheat code")))));

    address internal constant WETH = 0x4200000000000000000000000000000000000006;
    address internal constant USDC = 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913;

    uint256 internal constant START_WETH = 2e14;
    uint256 internal constant START_USDC = 500_000;
    uint256 internal constant FLASH_LIQ = 2_000_000;
    uint256 internal constant PRINCIPAL = 100_000;

    V124BestDex internal dex;
    V124BridgeVault internal ethBridge;
    V124BridgeVault internal usdcBridge;
    V124DebtBook internal debt;
    V124ZeroFeeFlashVault internal flash;
    V124QEExecutor internal exec;

    event LiveVenueQuotes(
        uint256 indexed blockNumber,
        uint256 uniswap,
        uint256 aerodromeClassic,
        uint256 aerodromeSlipstream,
        uint256 pancake,
        uint8 bestVenue,
        uint256 bestOut
    );

    event FiveCounters(
        uint256 indexed blockNumber,
        uint256 bridgeNavBefore,
        uint256 bridgeNavAfter,
        uint256 qeExecutorPnl,
        int256 qeCausalNav,
        uint256 qeDebtEnd,
        uint256 flashDebtEnd,
        bool residualZero,
        bool strictPass,
        uint8 venue
    );

    event PolicyDelta(uint256 indexed blockNumber, int256 qeTradeVsDoNothing, uint256 navBefore, uint256 navAfter);

    function setUp() public {
        vm.createSelectFork("https://base-rpc.publicnode.com");
        require(block.chainid == 8453, "NOT_BASE");

        dex = new V124BestDex();

        vm.deal(address(this), 1 ether);
        IWETHV124(WETH).deposit{value: 0.02 ether}();
        require(IERC20V124(WETH).approve(address(dex), type(uint256).max), "SETUP_APPROVE_WETH");

        (, uint256 usdcAcquired) = dex.swapBest(WETH, USDC, 0.005 ether, 30);
        require(usdcAcquired > START_USDC + FLASH_LIQ, "SETUP_USDC_TOO_SMALL");

        ethBridge = new V124BridgeVault(IERC20V124(WETH));
        usdcBridge = new V124BridgeVault(IERC20V124(USDC));
        debt = new V124DebtBook();
        flash = new V124ZeroFeeFlashVault(IERC20V124(USDC));
        exec = new V124QEExecutor(
            IERC20V124(USDC),
            IERC20V124(WETH),
            ethBridge,
            usdcBridge,
            debt,
            flash,
            dex
        );

        ethBridge.setController(address(exec));
        usdcBridge.setController(address(exec));
        debt.setController(address(exec));

        require(IERC20V124(WETH).transfer(address(ethBridge), START_WETH), "SEED_ETH_BRIDGE");
        require(IERC20V124(USDC).transfer(address(usdcBridge), START_USDC), "SEED_USDC_BRIDGE");
        require(IERC20V124(USDC).transfer(address(flash), FLASH_LIQ), "SEED_FLASH");
    }

    function testFork_LiveQuotes_UniswapAerodromePancake() public {
        V124BestDex.QuoteSet memory s = dex.quoteAll(USDC, WETH, PRINCIPAL);

        emit LiveVenueQuotes(
            block.number,
            s.uniswap,
            s.aerodromeClassic,
            s.aerodromeSlipstream,
            s.pancake,
            uint8(s.best.venue),
            s.best.amountOut
        );

        require(s.uniswap > 0, "UNI_NO_LIVE_QUOTE");
        require(s.aerodromeClassic > 0 || s.aerodromeSlipstream > 0, "AERO_NO_LIVE_QUOTE");
        require(s.pancake > 0, "PANCAKE_NO_LIVE_QUOTE");
        require(s.best.amountOut > 0, "NO_BEST_ROUTE");
    }

    function testFork_DistilledFiveCounters_QE10() public {
        uint256 navBefore = exec.bridgeNavExecutable();
        uint256 snap = vm.snapshotState();

        exec.run(PRINCIPAL, 0);
        uint256 navNoQEAfter = exec.bridgeNavExecutable();
        int256 deltaNoQE = _delta(navNoQEAfter, navBefore);

        require(vm.revertToState(snap), "REVERT_BASELINE");

        exec.run(PRINCIPAL, 1_000);
        uint256 navAfter = exec.bridgeNavExecutable();
        int256 deltaQE = _delta(navAfter, navBefore);
        int256 qeCausalNav = deltaQE - deltaNoQE;

        uint256 qeExecutorPnl = exec.lastExecutorPnl();
        uint256 qeDebtEnd = debt.debtUsd();
        uint256 flashDebtEnd = flash.outstanding();
        bool residualZero = IERC20V124(USDC).balanceOf(address(exec)) == 0
            && IERC20V124(WETH).balanceOf(address(exec)) == 0;

        bool strictPass = navAfter > navBefore && qeCausalNav > 0 && qeDebtEnd == 0 && flashDebtEnd == 0
            && residualZero;

        emit FiveCounters(
            block.number,
            navBefore,
            navAfter,
            qeExecutorPnl,
            qeCausalNav,
            qeDebtEnd,
            flashDebtEnd,
            residualZero,
            strictPass,
            uint8(exec.lastVenue())
        );

        require(qeExecutorPnl == PRINCIPAL / 10, "QE_EXECUTOR_PNL_WRONG");
        require(qeDebtEnd == 0, "QE_DEBT_NOT_ZERO");
        require(flashDebtEnd == 0, "FLASH_DEBT_NOT_ZERO");
        require(residualZero, "RESIDUAL_NOT_ZERO");

        require(navAfter == navNoQEAfter, "QE_CHANGED_CANONICAL_NAV");
        require(qeCausalNav == 0, "QE_CAUSAL_NAV_NONZERO");
    }

    function testFork_QETradeAgainstDoNothingBaseline_IsMeasuredNotAssumed() public {
        uint256 navBefore = exec.bridgeNavExecutable();

        exec.run(PRINCIPAL, 1_000);
        uint256 navAfter = exec.bridgeNavExecutable();
        int256 policyDelta = _delta(navAfter, navBefore);

        emit PolicyDelta(block.number, policyDelta, navBefore, navAfter);

        require(debt.debtUsd() == 0, "QE_DEBT_END");
        require(flash.outstanding() == 0, "FLASH_DEBT_END");
        require(IERC20V124(USDC).balanceOf(address(exec)) == 0, "USDC_RESIDUAL");
        require(IERC20V124(WETH).balanceOf(address(exec)) == 0, "WETH_RESIDUAL");
    }

    function testFork_QE0vsQE20_SameCanonicalNAV_DifferentExecutorPnL() public {
        uint256 navBefore = exec.bridgeNavExecutable();
        uint256 snap = vm.snapshotState();

        exec.run(PRINCIPAL, 0);
        uint256 nav0 = exec.bridgeNavExecutable();
        uint256 pnl0 = exec.lastExecutorPnl();

        require(vm.revertToState(snap), "REVERT_QE0");

        exec.run(PRINCIPAL, 2_000);
        uint256 nav20 = exec.bridgeNavExecutable();
        uint256 pnl20 = exec.lastExecutorPnl();

        require(nav20 == nav0, "QE20_CHANGED_NAV");
        require(pnl20 > pnl0, "QE20_DID_NOT_RAISE_EXEC_PNL");
        require(_delta(nav20, navBefore) == _delta(nav0, navBefore), "DELTA_MISMATCH");
    }

    function _delta(uint256 afterValue, uint256 beforeValue) internal pure returns (int256) {
        if (afterValue >= beforeValue) return int256(afterValue - beforeValue);
        return -int256(beforeValue - afterValue);
    }
}
