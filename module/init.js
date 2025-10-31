/* Dark Sun PF2E module bootstrap */

Hooks.once("init", () => {
  console.log("Dark Sun PF2E | Initialising module");
});

Hooks.once("ready", () => {
  if (game.system.id !== "pf2e") {
    ui.notifications?.warn("Dark Sun PF2E requires the Pathfinder Second Edition system.");
  }
});

