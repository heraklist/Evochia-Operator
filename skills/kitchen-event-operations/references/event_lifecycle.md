# Event Lifecycle

This reference defines the canonical operational lifecycle for private-chef, catering and event work. It is a workflow contract, not persistent event state.

```text
lead/enquiry
→ structured brief
→ feasibility
→ menu
→ recipes
→ production / staffing / equipment
→ procurement
→ event economics
→ client proposal
→ prep / packing / run sheet
→ service
→ close-out
→ actual vs estimated
→ approved learning
```

## Gate rules

- **Structured brief:** record known fields, unknowns, assumptions, dietary/allergen requirements, location, service format and constraints.
- **Feasibility:** do not declare the event feasible while critical kitchen, cold-chain, staffing, equipment, timing, transport or safety constraints remain unresolved.
- **Menu and recipes:** preserve culinary identity while validating serviceability, holding, regeneration, portion consistency and production load.
- **Production / staffing / equipment:** convert the menu into executable mise en place, production sequence, staffing responsibilities and equipment requirements.
- **Procurement:** derive purchasing needs from approved recipe/event quantities; supplier evidence remains source/date/confidence aware.
- **Event economics:** calculate food, labour, logistics, equipment, overhead, VAT and economic cost before client-safe commercial projection where applicable.
- **Client proposal:** expose only approved CLIENT-SAFE scope, menu, fee and terms; internal cost basis and strategy remain internal.
- **Prep / packing / run sheet:** create operationally ordered production, packing/loading, setup, service and recovery instructions.
- **Service:** protect food safety, timing, guest experience and recovery options. Novel interaction must never jeopardize successful dinner/service execution.
- **Close-out:** record actual versus estimated quantities, time, staffing, cost and operational issues.
- **Approved learning:** only validated learning is promoted into reusable doctrine or persistent operating records.

## Persistence boundary

Chef AI may structure, reason over and hand off event state, but it does not become a persistent event database. FnB Central remains the persistent structured operating system when used; external writes follow the controlled integration contract.
