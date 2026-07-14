export default function PoweredByFooter({ time }) {
  return (
    <div className="flex items-center justify-between text-[10px] text-muted-foreground uppercase tracking-wider font-medium">
      <span>Powered by Llama-3.3-70B</span>
      {time && <span>{time}s</span>}
    </div>
  )
}
