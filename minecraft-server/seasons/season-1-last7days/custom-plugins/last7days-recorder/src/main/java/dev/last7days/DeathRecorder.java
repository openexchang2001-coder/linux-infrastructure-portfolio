package dev.last7days;

import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.entity.EntityDamageEvent;
import org.bukkit.event.entity.PlayerDeathEvent;
import org.bukkit.plugin.java.JavaPlugin;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.time.Instant;

public final class DeathRecorder extends JavaPlugin implements Listener {

    @Override
    public void onEnable() {
        saveDefaultConfig();
        getServer().getPluginManager().registerEvents(this, this);
        getLogger().info("Death recorder enabled.");
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onDeath(PlayerDeathEvent event) {
        if (!getConfig().getBoolean("tracking-enabled", false)) {
            return;
        }

        Player player = event.getEntity();
        EntityDamageEvent damage = player.getLastDamageCause();

        String cause = damage == null
                ? "UNKNOWN"
                : damage.getCause().name();

        String season = getConfig()
                .getString("season-id", "dev-test")
                .replaceAll("[^A-Za-z0-9_-]", "_");

        String record = String.format(
                "{\"time_utc\":\"%s\",\"season\":\"%s\","
                + "\"uuid\":\"%s\",\"player\":\"%s\","
                + "\"cause\":\"%s\"}%n",
                Instant.now(),
                season,
                player.getUniqueId(),
                player.getName(),
                cause
        );

        try {
            Path file = getDataFolder().toPath()
                    .resolve("deaths-" + season + ".jsonl");

            Files.createDirectories(file.getParent());

            Files.writeString(
                    file,
                    record,
                    StandardCharsets.UTF_8,
                    StandardOpenOption.CREATE,
                    StandardOpenOption.APPEND
            );

            getLogger().info(
                    "Death recorded: " + player.getName()
            );

        } catch (IOException e) {
            getLogger().severe(
                    "Failed to save death event: " + e.getMessage()
            );
        }
    }
}
