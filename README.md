# Multi-Agent Coordination System for Automated Negotiation

## Overview
This project focuses on modeling a multi-agent system for automated negotiation, specifically in the context of travel organization. The system consists of two types of agents: **supplier agents** and **buyer agents**. Supplier agents are responsible for gathering information about services, preferences, and constraints from service providers (e.g., airlines or train companies). Buyer agents represent individuals or organizations seeking to acquire services or goods, and they collect necessary information to conduct negotiations on behalf of their users.

The goal of this project is to simulate and analyze the behavior of these agents during negotiations, including individual decision-making, communication, and group behaviors such as coalition formation. The project also explores the impact of different strategies on price evolution and gains.

## Project Structure

### Agent Types
1. **Supplier Agents**:
   - Responsible for managing services (e.g., flight or train tickets) provided by service providers.
   - Handle constraints such as minimum prices, latest sale dates, and preferences like preferred sale dates.
   - Example: An airline submits a set of flight tickets to a supplier agent for sale.

2. **Buyer Agents**:
   - Represent individuals or organizations looking to purchase services or goods.
   - Collect preferences and constraints from their users (e.g., budget limits, preferred airlines, latest purchase dates).
   - Example: A user provides a buyer agent with a budget constraint (e.g., less than 600 euros for a flight ticket).

### Key Features
- **Negotiation Strategies**:
  - Buyers and suppliers can adopt different strategies for negotiation, such as aggressive, conciliatory, or default strategies.
  - Strategies are influenced by user preferences, constraints, and negotiation parameters (e.g., initial offer value, offer frequency, and growth rate of offers).

- **Coalition Formation**:
  - Agents can form coalitions to improve their negotiation power.
  - Different algorithms are implemented for coalition formation:
    - **Competitive Mode**: Algorithms like matching-based coalition formation without information sharing.
    - **Cooperative Mode**: Algorithms like IDP (Improved Dynamic Programming) and IP (Incremental Programming) that use dynamic programming with information sharing.
    - **Token-Based Coalition Formation**: Agents form coalitions cooperatively by sharing information through tokens that circulate among agents.

- **Coalition Value**:
  - The value of a coalition is determined by a function that considers factors such as user profiles, past purchases, constraints, and preferred dates.
  - The coalition value influences the discounts or benefits that members can obtain during negotiations.

## Implementation

### Files and Classes
- **Agent Classes**:
  - `Supplier`: Implements supplier agents with specific negotiation strategies.
  - `Buyer`: Implements buyer agents with specific negotiation strategies.
  - `Agent`: Base class for all agents, handling common functionalities like message passing and negotiation.

- **Negotiation and Communication**:
  - `Message`: Defines the structure of messages exchanged between agents.
  - `SharedMessageBoard`: Implements a shared message board for communication between agents.

- **Strategies**:
  - `Strategies`: Contains predefined negotiation strategies for both buyers and suppliers (e.g., default, aggressive, conciliatory).

- **Coalition Formation**:
  - `Coalition`: Implements coalition formation algorithms and calculates coalition values.
  - Algorithms include IDP, IP, and token-based coalition formation.

