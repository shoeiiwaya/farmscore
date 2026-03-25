"use client";

import { useEffect, useRef } from "react";
import L from "leaflet";

interface MapPickerProps {
  lat: number;
  lon: number;
  onLocationChange: (lat: number, lon: number) => void;
  score?: number;
  grade?: string;
}

export default function MapPicker({ lat, lon, onLocationChange, score, grade }: MapPickerProps) {
  const mapRef = useRef<L.Map | null>(null);
  const markerRef = useRef<L.Marker | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const map = L.map(containerRef.current, {
      center: [lat, lon],
      zoom: 10,
      zoomControl: true,
    });

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; OpenStreetMap contributors",
    }).addTo(map);

    // Add GSI pale tile as overlay option
    const gsiPale = L.tileLayer(
      "https://cyberjapandata.gsi.go.jp/xyz/pale/{z}/{x}/{y}.png",
      { attribution: "&copy; 国土地理院", maxZoom: 18 }
    );

    L.control.layers(
      {
        OpenStreetMap: L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"),
        "地理院 淡色": gsiPale,
        "地理院 写真": L.tileLayer(
          "https://cyberjapandata.gsi.go.jp/xyz/seamlessphoto/{z}/{x}/{y}.jpg",
          { attribution: "&copy; 国土地理院", maxZoom: 18 }
        ),
      },
      {},
      { position: "topright" }
    ).addTo(map);

    const marker = L.marker([lat, lon], { draggable: true }).addTo(map);

    marker.on("dragend", () => {
      const pos = marker.getLatLng();
      onLocationChange(Math.round(pos.lat * 10000) / 10000, Math.round(pos.lng * 10000) / 10000);
    });

    map.on("click", (e: L.LeafletMouseEvent) => {
      const { lat: newLat, lng: newLon } = e.latlng;
      marker.setLatLng([newLat, newLon]);
      onLocationChange(Math.round(newLat * 10000) / 10000, Math.round(newLon * 10000) / 10000);
    });

    mapRef.current = map;
    markerRef.current = marker;

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Update marker position when props change
  useEffect(() => {
    if (markerRef.current) {
      markerRef.current.setLatLng([lat, lon]);
    }
    if (mapRef.current) {
      mapRef.current.setView([lat, lon], mapRef.current.getZoom());
    }
  }, [lat, lon]);

  // Update popup
  useEffect(() => {
    if (markerRef.current && score !== undefined && grade) {
      markerRef.current
        .bindPopup(
          `<div class="text-center">
            <div class="text-2xl font-bold">${Math.round(score)}<span class="text-sm">点</span></div>
            <div class="text-lg font-semibold">グレード ${grade}</div>
            <div class="text-xs text-gray-500">${lat}, ${lon}</div>
          </div>`,
          { className: "farm-popup" }
        )
        .openPopup();
    }
  }, [score, grade, lat, lon]);

  return (
    <div
      ref={containerRef}
      className="w-full h-[500px] rounded-xl border border-gray-200 shadow-sm"
    />
  );
}
