"use client";
import { useMemo } from "react";
import { ReactFlow, Background, Controls, MiniMap, type Node, type Edge } from "@xyflow/react";
import { useStore } from "@/store";
import { nodeTypes } from "./NodeTypes";
import { layoutGraph } from "@/lib/graphLayout";

export function LegalGraph() {
  const graph = useStore((s) => s.graph);

  const { nodes, edges } = useMemo(() => {
    if (!graph) return { nodes: [] as Node[], edges: [] as Edge[] };

    const rfNodes: Node[] = graph.nodes.map((n) => ({
      id: n.id,
      type: n.type,
      position: { x: 0, y: 0 },
      data: { label: n.label, data: n.data, is_gap: n.is_gap },
    }));

    const rfEdges: Edge[] = graph.edges.map((e) => ({
      id: e.id,
      source: e.source,
      target: e.target,
      animated: e.animated,
      className:
        e.type === "MAPS_TO"
          ? "edge-maps"
          : e.type === "CONFLICTS_WITH"
            ? "edge-conflicts"
            : e.type === "ENFORCED_BY"
              ? "edge-enforces"
              : "edge-contains",
      label: e.type,
      labelStyle: { fontSize: 9, fill: "#6B7280" },
    }));

    return layoutGraph(rfNodes, rfEdges, "LR");
  }, [graph]);

  if (!graph || graph.nodes.length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-ink/40 text-sm">
        Select a contract to view its legal graph.
      </div>
    );
  }

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      nodeTypes={nodeTypes}
      fitView
      proOptions={{ hideAttribution: true }}
      defaultEdgeOptions={{ type: "default" }}
    >
      <Background gap={20} size={1} color="#E5E4DE" />
      <MiniMap pannable zoomable />
      <Controls showInteractive={false} />
    </ReactFlow>
  );
}
