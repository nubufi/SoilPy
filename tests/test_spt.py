"""Tests for SPT (Standard Penetration Test) model functions."""

import pytest

from soilpy.enums import SelectionMethod
from soilpy.models import SoilLayer, SoilProfile
from soilpy.models.spt import SPT, NValue, SPTBlow, SPTExp


class TestNValue:
    """Test cases for NValue class."""

    def test_nvalue_from_i32(self):
        """Test NValue creation from int."""
        assert NValue.from_i32(10) == NValue(value=10)

    def test_nvalue_to_i32(self):
        """Test NValue conversion to int."""
        assert NValue(value=10).to_i32() == 10
        assert NValue(value=0).to_i32() == 0
        assert NValue(value="R").to_i32() == 50

    def test_nvalue_mul_by_f64(self):
        """Test NValue multiplication by float."""
        assert NValue(value=10).mul_by_f64(2.0) == NValue(value=20)
        assert NValue(value=5).mul_by_f64(2.5) == NValue(
            value=13
        )  # 5 * 2.5 = 12.5 -> truncated to 13
        assert NValue(value="R").mul_by_f64(3.0) == NValue(value="R")

    def test_nvalue_sum_with(self):
        """Test NValue addition with another NValue."""
        assert NValue(value=10).sum_with(NValue(value=5)) == NValue(value=15)
        assert NValue(value=0).sum_with(NValue(value=0)) == NValue(value=0)
        assert NValue(value=10).sum_with(NValue(value="R")) == NValue(value="R")
        assert NValue(value="R").sum_with(NValue(value=5)) == NValue(value="R")
        assert NValue(value="R").sum_with(NValue(value="R")) == NValue(value="R")

    def test_nvalue_add_f64(self):
        """Test NValue addition with float."""
        assert NValue(value=10).add_f64(5.5) == NValue(
            value=16
        )  # 10 + 5.5 -> truncated to 16
        assert NValue(value=3).add_f64(1.9) == NValue(
            value=5
        )  # 3 + 1.9 -> truncated to 5
        assert NValue(value="R").add_f64(5.0) == NValue(value="R")

    def test_nvalue_default(self):
        """Test NValue default value."""
        assert NValue(value=0) == NValue(value=0)

    def test_nvalue_display(self):
        """Test NValue string representation."""
        assert str(NValue(value=42)) == "42"
        assert str(NValue(value="R")) == "R"

    def test_nvalue_ordering(self):
        """Test NValue comparison operations."""
        assert NValue(value="R") > NValue(value=1000)
        assert NValue(value="R") > NValue(value=0)
        assert NValue(value="R") > NValue(value=-50)
        assert NValue(value=10) > NValue(value=5)
        assert NValue(value=5) < NValue(value=10)
        assert NValue(value="R") == NValue(value="R")
        assert NValue(value=10) == NValue(value=10)


class TestSPTBlow:
    """Test cases for SPTBlow class."""

    def test_sptblow_new(self):
        """Test SPTBlow creation."""
        spt = SPTBlow.new(10.0, NValue(value=25))

        assert spt.depth == 10.0
        assert spt.n == NValue(value=25)
        assert spt.n60 is None
        assert spt.n90 is None
        assert spt.n1_60 is None
        assert spt.n1_60f is None
        assert spt.cn is None
        assert spt.alpha is None
        assert spt.beta is None

    def test_apply_energy_correction(self):
        """Test energy correction application."""
        spt = SPTBlow.new(10.0, NValue(value=25))
        spt.apply_energy_correction(1.2)

        assert spt.n60 == NValue(value=30)  # 25 * 1.2 = 30
        assert spt.n90 == NValue(value=45)  # 30 * 1.5 = 45

    def test_set_cn(self):
        """Test overburden correction factor setting."""
        spt = SPTBlow.new(10.0, NValue(value=25))
        spt.set_cn(0.5)

        expected_cn = min((1.0 / (9.81 * 0.5)) ** 0.5 * 9.78, 1.7)
        assert abs(spt.cn - expected_cn) < 0.001

    def test_set_alpha_beta(self):
        """Test alpha and beta factors setting."""
        spt = SPTBlow.new(10.0, NValue(value=25))

        spt.set_alpha_beta(4.0)
        assert spt.alpha == 0.0
        assert spt.beta == 1.0

        spt.set_alpha_beta(10.0)
        assert abs(spt.alpha - 0.869) < 0.001
        assert abs(spt.beta - 1.021) < 0.1

        spt.set_alpha_beta(40.0)
        assert spt.alpha == 5.0
        assert spt.beta == 1.2

    def test_apply_corrections(self):
        """Test applying all corrections."""
        spt = SPTBlow.new(10.0, NValue(value=25))

        soil_profile = SoilProfile(
            layers=[
                SoilLayer(
                    thickness=10.0,
                    dry_unit_weight=1.8,
                    saturated_unit_weight=2.0,
                    fine_content=10.0,
                )
            ],
            ground_water_level=10.0,
        )
        cs = 0.9
        cb = 1.05
        ce = 1.2

        spt.apply_corrections(soil_profile, cs, cb, ce)

        assert spt.n60.to_i32() == 30
        assert spt.n90.to_i32() == 45
        assert abs(spt.cn - 0.735) < 0.001
        assert abs(spt.alpha - 0.869) < 0.001
        assert abs(spt.beta - 1.021) < 0.1
        assert spt.n1_60.to_i32() == 20
        assert spt.n1_60f.to_i32() == 22


class TestSPT:
    """Test cases for SPT class."""

    def test_get_idealized_exp(self):
        """Test idealized experiment creation."""
        exp1 = SPTExp.new([], "exp1")
        exp1.add_blow(1.5, NValue(value=10))
        exp1.add_blow(2.0, NValue(value=20))
        exp1.add_blow(3.0, NValue(value="R"))

        exp2 = SPTExp.new([], "exp2")
        exp2.add_blow(1.5, NValue(value=15))
        exp2.add_blow(3.0, NValue(value=14))

        cs = 0.9
        cb = 1.05
        ce = 1.2
        spt = SPT.new(ce, cb, cs, SelectionMethod.MIN)
        spt.add_exp(exp1)
        spt.add_exp(exp2)

        idealized_exp_min = spt.get_idealized_exp("idealized_exp_min")

        spt.idealization_method = SelectionMethod.AVG
        idealized_exp_avg = spt.get_idealized_exp("idealized_exp_avg")

        spt.idealization_method = SelectionMethod.MAX
        idealized_exp_max = spt.get_idealized_exp("idealized_exp_max")

        assert idealized_exp_min.name == "idealized_exp_min"
        assert idealized_exp_avg.name == "idealized_exp_avg"
        assert idealized_exp_max.name == "idealized_exp_max"

        assert len(idealized_exp_min.blows) == 3
        assert len(idealized_exp_avg.blows) == 3
        assert len(idealized_exp_max.blows) == 3

        assert idealized_exp_min.blows[0].depth == 1.5
        assert idealized_exp_min.blows[1].depth == 2.0
        assert idealized_exp_min.blows[2].depth == 3.0

        assert idealized_exp_avg.blows[0].depth == 1.5
        assert idealized_exp_avg.blows[1].depth == 2.0
        assert idealized_exp_avg.blows[2].depth == 3.0

        assert idealized_exp_max.blows[0].depth == 1.5
        assert idealized_exp_max.blows[1].depth == 2.0
        assert idealized_exp_max.blows[2].depth == 3.0

        assert idealized_exp_min.blows[0].n == NValue(value=10)
        assert idealized_exp_min.blows[1].n == NValue(value=20)
        assert idealized_exp_min.blows[2].n == NValue(value=14)

        assert idealized_exp_avg.blows[0].n == NValue(value=13)
        assert idealized_exp_avg.blows[1].n == NValue(value=20)
        assert idealized_exp_avg.blows[2].n == NValue(value=32)

        assert idealized_exp_max.blows[0].n == NValue(value=15)
        assert idealized_exp_max.blows[1].n == NValue(value=20)
        assert idealized_exp_max.blows[2].n == NValue(value="R")
