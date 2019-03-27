#! /usr/bin/env python3

import unittest

import torch
from botorch.utils import apply_constraints, get_objective_weights_transform
from torch import Tensor


def ones_f(samples: Tensor) -> Tensor:
    return torch.ones(samples.shape[0:-1], device=samples.device, dtype=samples.dtype)


def zeros_f(samples: Tensor) -> Tensor:
    return torch.zeros(samples.shape[0:-1], device=samples.device, dtype=samples.dtype)


def minus_one_f(samples: Tensor) -> Tensor:
    return -torch.ones(samples.shape[0:-1], device=samples.device, dtype=samples.dtype)


class TestApplyConstraints(unittest.TestCase):
    def test_apply_constraints(self):
        # nonnegative objective, one constraint
        samples = torch.randn(1)
        obj = ones_f(samples)
        obj = apply_constraints(
            obj=obj, constraints=[zeros_f], samples=samples, infeasible_cost=0.0
        )
        self.assertTrue(torch.equal(obj, ones_f(samples) * 0.5))
        # nonnegative objective, two constraint
        samples = torch.randn(1)
        obj = ones_f(samples)
        obj = apply_constraints(
            obj=obj,
            constraints=[zeros_f, zeros_f],
            samples=samples,
            infeasible_cost=0.0,
        )
        self.assertTrue(torch.equal(obj, ones_f(samples) * 0.5 * 0.5))
        # negative objective, one constraint, infeasible_cost
        samples = torch.randn(1)
        obj = minus_one_f(samples)
        obj = apply_constraints(
            obj=obj, constraints=[zeros_f], samples=samples, infeasible_cost=2.0
        )
        self.assertTrue(torch.equal(obj, ones_f(samples) * 0.5 - 2.0))


class TestGetObjectiveWeightsTransform(unittest.TestCase):
    def test_NoWeights(self):
        Y = torch.ones(5, 2, 4)
        objective_transform = get_objective_weights_transform(None)
        Y_transformed = objective_transform(Y)
        self.assertTrue(torch.equal(Y, Y_transformed))

    def test_OneWeightBroadcasting(self):
        Y = torch.ones(5, 2, 4)
        objective_transform = get_objective_weights_transform(torch.tensor([0.5]))
        Y_transformed = objective_transform(Y)
        self.assertTrue(torch.equal(0.5 * Y.sum(dim=-1), Y_transformed))

    def test_IncompatibleNumberOfWeights(self):
        Y = torch.ones(5, 2, 4)
        objective_transform = get_objective_weights_transform(torch.tensor([1.0, 2.0]))
        with self.assertRaises(RuntimeError):
            objective_transform(Y)

    def test_MultiTaskWeights(self):
        Y = torch.ones(5, 2, 4, 2)
        objective_transform = get_objective_weights_transform(torch.tensor([1.0, 1.0]))
        Y_transformed = objective_transform(Y)
        self.assertTrue(torch.equal(torch.sum(Y, dim=-1), Y_transformed))

    def test_NoMCSamples(self):
        Y = torch.ones(2, 4, 2)
        objective_transform = get_objective_weights_transform(torch.tensor([1.0, 1.0]))
        Y_transformed = objective_transform(Y)
        self.assertTrue(torch.equal(torch.sum(Y, dim=-1), Y_transformed))