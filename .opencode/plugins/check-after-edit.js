import { appendFile, mkdir } from "node:fs/promises"
import { join } from "node:path"

const watchedTools = new Set(["write", "edit", "patch"])

export default {
  id: "practice.check-after-edit",

  async setup(ctx) {
    const root = ctx.location.project?.directory ?? ctx.location.directory

    await ctx.tool.hook("execute.after", async (event) => {
      if (event.status !== "completed" || !watchedTools.has(event.tool)) return

      const lines = [`[auto-check] tool=${event.tool}`]

      try {
        // Запускается фиксированная команда из репозитория.
        const child = Bun.spawn(["sh", "scripts/check.sh"], {
          cwd: root,
          stdout: "pipe",
          stderr: "pipe",
        })

        const [stdout, stderr, exitCode] = await Promise.all([
          new Response(child.stdout).text(),
          new Response(child.stderr).text(),
          child.exited,
        ])

        lines.push(`exit code: ${exitCode}`)
        if (stdout.trim()) lines.push(stdout.trim())
        if (stderr.trim()) lines.push(stderr.trim())

        // В журнал попадают только имя инструмента и exit code, без исходников.
        const logDir = join(root, "practices/practice_04/artifacts")
        await mkdir(logDir, { recursive: true })
        await appendFile(
          join(logDir, "hook.log"),
          `${new Date().toISOString()} tool=${event.tool} exit=${exitCode}\n`,
        )
      } catch (error) {
        lines.push(`Не удалось выполнить проверку: ${String(error)}`)
      }

      // Результат попадёт в контекст агента.
      event.content.push({ type: "text", text: lines.join("\n") })
    })
  },
}
