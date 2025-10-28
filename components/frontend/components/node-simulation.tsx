import React, { useEffect, useRef } from "react";
import * as d3 from "d3";

// Interface voor een node in de simulatie
interface Node {
  id: string;
  // fx en fy worden gebruikt om een node eventueel vast te zetten
  fx?: number;
  fy?: number;
  // x en y worden automatisch toegevoegd door D3 tijdens de simulatie
  x?: number;
  y?: number;
}

// Interface voor een link (relatie) tussen twee nodes
interface Link {
  source: string | Node;
  target: string | Node;
}

export const NodeSimulation: React.FC = () => {
  // useRef om een referentie naar het SVG-element te bewaren
  const svgRef = useRef<SVGSVGElement | null>(null);

  useEffect(() => {
    // Breedte en hoogte van de SVG-canvas
    const width = 600;
    const height = 400;

    /*
      DEFINITIE VAN DE DATA:
      We kiezen drie elementen op basis van hun @id.
      Hieronder worden ze omgezet in nodes.
      Ter overzichtelijkheid hebben we de namen kort weergegeven.
    */
    const nodes: Node[] = [
      { id: "Article (BWBR0045754/16046034)" },
      { id: "Wet (BWBR0045754/16045964)" },
      { id: "Onderdeel (BWBR0045754/16045024)" },
    ];

    /*
      DEFINITIE VAN DE RELATIES (links):
      In dit voorbeeld is "Article" de centrale node, die wordt verbonden met "Wet" en "Onderdeel".
    */
    const links: Link[] = [
      {
        source: "Article (BWBR0045754/16046034)",
        target: "Wet (BWBR0045754/16045964)",
      },
      {
        source: "Article (BWBR0045754/16046034)",
        target: "Onderdeel (BWBR0045754/16045024)",
      },
    ];

    // Maak of selecteer de SVG-canvas waarin de simulatie wordt getekend
    const svg = d3
      .select(svgRef.current)
      .attr("width", width)
      .attr("height", height);

    // Verwijder bestaande elementen (handig bij her-rendering)
    svg.selectAll("*").remove();

    /*
      SETUP VAN DE FORCE SIMULATIE:
      - forceLink zorgt voor de verbindingen tussen nodes.
      - forceManyBody creëert een afstotende kracht zodat de nodes niet samenklitten.
      - forceCenter trekt de simulatie naar het midden van de canvas.
    */
    const simulation = d3
      .forceSimulation(nodes)
      .force(
        "link",
        d3
          .forceLink(links)
          // @ts-expect-error d3 typing issue with id accessor
          .id((d) => d.id)
          .distance(150)
      )
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2));

    // TEKEN DE LINKS: De lijnen tussen nodes
    const link = svg
      .append("g")
      .attr("stroke", "#999")
      .attr("stroke-opacity", 0.6)
      .selectAll("line")
      .data(links)
      .enter()
      .append("line")
      .attr("stroke-width", 10);

    // TEKEN DE NODES: De rechthoeken die de elementen voorstellen
    const node = svg
      .append("g")
      .attr("stroke", "#fff")
      .attr("stroke-width", 1.5)
      .selectAll("rect")
      .data(nodes)
      .enter()
      .append("rect")
      .attr("width", 40) // Set rectangle width
      .attr("height", 40) // Set rectangle height
      .attr("rx", 10) // Stel de border radius in op 10 pixels
      .attr("fill", "#69b3a2")
      // Voeg drag-functionaliteit toe zodat nodes gesleept kunnen worden
      .call(
        d3
          .drag<SVGRectElement, Node>()
          .on("start", (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on("drag", (event, d) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on("end", (event, d) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = undefined;
            d.fy = undefined;
          })
      );

    // TEKEN TEKSTLABELS: Beschrijf elke node met een tekstlabel
    const label = svg
      .append("g")
      .selectAll("text")
      .data(nodes)
      .enter()
      .append("text")
      .text((d) => d.id)
      .attr("font-size", 10)
      .attr("dx", 25) // offset naar rechts van de node
      .attr("dy", 4); // verticale offset

    // Update de posities van nodes en links tijdens elke "tick" van de simulatie
    simulation.on("tick", () => {
      // Update de positie van de links (lijnen)
      link
        .attr("x1", (d) => (d.source as Node).x!)
        .attr("y1", (d) => (d.source as Node).y!)
        .attr("x2", (d) => (d.target as Node).x!)
        .attr("y2", (d) => (d.target as Node).y!);

      // Update de positie van de nodes (rechthoeken) met offset zodat ze gecentreerd liggen
      node
        .attr("x", (d) => d.x! - 20) // 20 is de helft van de rectangle breedte (40)
        .attr("y", (d) => d.y! - 20); // 20 is de helft van de rectangle hoogte (40)

      // Update de positie van de labels (optioneel aanpassen indien gewenst)
      label.attr("x", (d) => d.x!).attr("y", (d) => d.y!);
    });

    // Opruimen: stop de simulatie als het component wordt ontmanteld
    return () => {
      simulation.stop();
    };
  }, []);

  // Render de hoofdcontainer met het SVG-element waarin D3 de simulatie tekent.
  return (
    <div>
      <svg ref={svgRef}></svg>
    </div>
  );
};
